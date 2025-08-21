import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse
from datetime import date

from courses.models import (
    Course, Section, Semester, Room, Department, Faculty, Profile
)

# ----------
# URL names 
# ----------
URL_SECTION_LIST   = "courses:section-list"    # args=[course.id]
URL_SECTION_ADD    = "courses:section-add"     # args=[course.id]
URL_SECTION_EDIT   = "courses:section-edit"    # args=[section.id]
URL_SECTION_DELETE = "courses:section-delete"  # args=[section.id]


# ----------------
# Fixtures พื้นฐาน
# ----------------
@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="วิทยาศาสตร์")

@pytest.fixture
def department(db, faculty):
    return Department.objects.create(name="คอมพิวเตอร์", faculty=faculty)

@pytest.fixture
def course(db, department):
    # ใช้โค้ด 6 หลัก (ตรงตาม validator ของโปรเจกต์)
    return Course.objects.create(
        code="123456",
        name="Programming",
        department=department,
        credits=3,
        is_active=True,
    )

@pytest.fixture
def semester(db):
    return Semester.objects.create(
        year=2567, semester=1,
        start_date=date(2025, 6, 1), end_date=date(2025, 10, 1)
    )

@pytest.fixture
def room(db):
    return Room.objects.create(building="A", room_number="101")  # A-101

@pytest.fixture
def staff_group(db):
    return Group.objects.get_or_create(name="staff")[0]

@pytest.fixture
def instructor_group(db):
    return Group.objects.get_or_create(name="instructor")[0]

@pytest.fixture
def staff_user(db, staff_group):
    user = User.objects.create_user(username="admin", password="123456789", is_staff=True)
    user.groups.add(staff_group)
    Profile.objects.create(user=user, user_type='ADMIN')
    return user

@pytest.fixture
def instructor_user(db, instructor_group):
    user = User.objects.create_user(username="instructor", password="pass123")
    user.groups.add(instructor_group)
    Profile.objects.create(user=user, user_type='INSTRUCTOR')
    return user

@pytest.fixture
def section(db, course, semester, room, instructor_user):
    s = Section.objects.create(
        course=course, section_number="1", semester=semester, room=room, capacity=30
    )
    s.instructors.add(instructor_user)
    return s


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _login_staff(client, user):
    client.force_login(user)

def _url_section_list(course):
    return reverse(URL_SECTION_LIST, args=[course.id])

def _url_section_add(course):
    return reverse(URL_SECTION_ADD, args=[course.id])

def _url_section_edit(section):
    return reverse(URL_SECTION_EDIT, args=[section.id])

def _url_section_delete(section):
    return reverse(URL_SECTION_DELETE, args=[section.id])

def _section_payload(semester, room, instructor_user, **overrides):
    """
    payload พื้นฐานสำหรับ SectionForm + inline formset class_times (0 แถว)
    """
    base = {
        "semester": semester.id,
        "section_number": "1",
        "room": room.id,
        "capacity": 30,
        "instructors": [str(instructor_user.id)],
        # management form ของ class_times formset
        "class_times-TOTAL_FORMS": 0,
        "class_times-INITIAL_FORMS": 0,
        "class_times-MIN_NUM_FORMS": 0,
        "class_times-MAX_NUM_FORMS": 1000,
    }
    base.update(overrides)
    return base

def _post_section_add(client, course, semester, room, instructor_user, **overrides):
    url = _url_section_add(course)
    data = _section_payload(semester, room, instructor_user, **overrides)
    return client.post(url, data)

def _post_section_edit(client, section, **overrides):
    url = _url_section_edit(section)
    # รวมค่า default ของฟอร์มแก้ไขไว้ใน dict เดียว แล้วค่อย update ด้วย overrides
    base_overrides = {
        "section_number": section.section_number,
        "capacity": section.capacity,
    }
    base_overrides.update(overrides)

    data = _section_payload(
        semester=section.semester,
        room=section.room,
        instructor_user=section.instructors.first(),
        **base_overrides
    )
    return client.post(url, data)

# SEC-001: เข้าหน้าจัดกลุ่มจากรายวิชา
@pytest.mark.django_db
def test_SEC_001_enter_section_page_from_course(client, staff_user, course):
    _login_staff(client, staff_user)
    resp = client.get(_url_section_list(course))
    assert resp.status_code == 200

# SEC-002: เพิ่ม Section สำเร็จ
@pytest.mark.django_db
def test_SEC_002_section_add_success(client, staff_user, course, semester, room, instructor_user):
    _login_staff(client, staff_user)
    resp = _post_section_add(client, course, semester, room, instructor_user)
    assert resp.status_code in (302, 303)
    assert Section.objects.filter(course=course, semester=semester, section_number="1").exists()

# SEC-003: เพิ่ม Section (Negative: ซ้ำ)
@pytest.mark.django_db
def test_SEC_003_section_add_duplicate(client, staff_user, course, semester, room, instructor_user):
    _login_staff(client, staff_user)
    # สร้างตัวแรก
    Section.objects.create(course=course, semester=semester, room=room, section_number="1", capacity=30).instructors.add(instructor_user)
    # โพสต์ค่าเดิมซ้ำ
    resp = _post_section_add(client, course, semester, room, instructor_user, section_number="1")
    assert resp.status_code == 200
    # ฟอร์มต้องมี error (อย่างน้อยที่ฟิลด์ section_number)
    assert "section_number" in resp.context["form"].errors


# -------------------------------------------------------------------
# SEC-004: เพิ่ม Section (Negative: capacity/required)
#   กรณี: capacity = 0, -1, 'abc'
#   กรณี: ไม่เลือก semester / room
# -------------------------------------------------------------------
@pytest.mark.django_db
@pytest.mark.parametrize("bad_payload, expected_error_field", [
    ({"capacity": 0}, "capacity"),
    ({"capacity": -1}, "capacity"),
    ({"capacity": "abc"}, "capacity"),
    ({"semester": ""}, "semester"),
    ({"room": ""}, "room"),
])
def test_SEC_004_section_add_invalid(client, staff_user, course, semester, room, instructor_user, bad_payload, expected_error_field):
    _login_staff(client, staff_user)
    url = _url_section_add(course)

    # สร้าง payload พื้นฐาน แล้วค่อย update ด้วย bad_payload ที่อยากทดสอบ
    data = _section_payload(semester, room, instructor_user)
    data.update(bad_payload)

    resp = client.post(url, data)
    assert resp.status_code == 200
    assert expected_error_field in resp.context["form"].errors

# SEC-005: แก้ไข Section สำเร็จ (แก้ capacity)
@pytest.mark.django_db
def test_SEC_005_section_edit_success(client, staff_user, section):
    _login_staff(client, staff_user)
    resp = _post_section_edit(client, section, capacity=40)
    assert resp.status_code in (302, 303)
    section.refresh_from_db()
    assert section.capacity == 40

# -------------------------------------------------------------------
# SEC-006: แก้ไข Section (Negative: ทำให้ซ้ำ)
# มี '1' และ '2' ในภาคเรียนเดียวกัน -> แก้ '2' ให้กลายเป็น '1' (ซ้ำ)
# -------------------------------------------------------------------
@pytest.mark.django_db
def test_SEC_006_section_edit_to_duplicate(client, staff_user, course, semester, room, instructor_user):
    _login_staff(client, staff_user)
    sec1 = Section.objects.create(course=course, semester=semester, room=room, section_number="1", capacity=30)
    sec1.instructors.add(instructor_user)
    sec2 = Section.objects.create(course=course, semester=semester, room=room, section_number="2", capacity=30)
    sec2.instructors.add(instructor_user)

    resp = _post_section_edit(client, sec2, section_number="1")
    assert resp.status_code == 200
    assert "section_number" in resp.context["form"].errors


# -------------------------------------------------------------------
# SEC-007: ลบ Section (Confirm/Cancel)
# หมายเหตุ: แยกเป็น 2 เทสต์ให้ชัดเจนตามพฤติกรรม UI ปัจจุบัน
#   - Confirm: POST ไปที่หน้า delete -> ควรถูกลบ และ redirect
#   - Cancel:  กดลิงก์กลับ list (GET) -> ไม่ถูกลบ
# -------------------------------------------------------------------

# Confirm delete
@pytest.mark.django_db
def test_SEC_007A_section_delete_confirm(client, staff_user, section):
    _login_staff(client, staff_user)
    url = _url_section_delete(section)
    resp = client.post(url, {})  # POST ยืนยันลบ
    assert resp.status_code in (302, 303)
    assert not Section.objects.filter(id=section.id).exists()

# Cancel delete via link (ไม่โพสต์ cancel)
@pytest.mark.django_db
def test_SEC_007B_section_delete_cancel_via_link(client, staff_user, section):
    _login_staff(client, staff_user)
    # เปิดหน้า confirm ก่อน (ไม่จำเป็นแต่ทำให้ชัดว่าเราอยู่หน้าลบ)
    resp = client.get(_url_section_delete(section))
    assert resp.status_code in (200, 302, 303)  # บางโปรเจกต์อาจ redirect ไป login ถ้าไม่ได้ล็อกอิน

    # กดลิงก์ "ยกเลิก" = กลับไปหน้า list
    resp = client.get(_url_section_list(section.course))
    assert resp.status_code == 200
    # ไม่ควรถูกลบ
    assert Section.objects.filter(id=section.id).exists()
