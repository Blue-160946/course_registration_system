# courses/tests/test_ClassTime_integration.py
import pytest
from datetime import date, time

from django.contrib.auth.models import User, Group
from django.urls import reverse

from courses.models import (
    Faculty, Department, Course, Semester, Room, Section, ClassTime, Profile
)

# -------------------------------------------------------------------
# URL names 
# -------------------------------------------------------------------
URL_CT_ADD    = "courses:time-add"     # args=[section.id]
URL_CT_EDIT   = "courses:time-edit"    # args=[ct.id]
URL_CT_DELETE = "courses:time-delete"  # args=[ct.id]

# ========================= Fixtures พื้นฐาน =========================
@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="วิทยาศาสตร์")

@pytest.fixture
def department(db, faculty):
    return Department.objects.create(name="คอมพิวเตอร์", faculty=faculty)

@pytest.fixture
def course(db, department):
    return Course.objects.create(code="123456", name="Programming",
                                 department=department, credits=3, is_active=True)

@pytest.fixture
def semester(db):
    return Semester.objects.create(
        year=2567, semester=1,
        start_date=date(2024, 8, 1), end_date=date(2024, 12, 31)
    )

@pytest.fixture
def semester_next(db):
    return Semester.objects.create(
        year=2568, semester=1,
        start_date=date(2025, 8, 1), end_date=date(2025, 12, 31)
    )

@pytest.fixture
def room_a(db):
    return Room.objects.create(building="A", room_number="101")

@pytest.fixture
def room_b(db):
    return Room.objects.create(building="B", room_number="201")

@pytest.fixture
def staff_group(db):
    return Group.objects.get_or_create(name="staff")[0]

@pytest.fixture
def instructor_group(db):
    return Group.objects.get_or_create(name="instructor")[0]

@pytest.fixture
def student_group(db):
    return Group.objects.get_or_create(name="student")[0]

@pytest.fixture
def staff_user(db, staff_group):
    u = User.objects.create_user(username="admin", password="pass123", is_staff=True)
    u.groups.add(staff_group)
    Profile.objects.create(user=u, user_type="ADMIN")
    return u

@pytest.fixture
def instructor_user(db, instructor_group):
    u = User.objects.create_user(username="instructor", password="pass123")
    u.groups.add(instructor_group)
    Profile.objects.create(user=u, user_type="INSTRUCTOR")
    return u

@pytest.fixture
def student_user(db, student_group):
    u = User.objects.create_user(username="student1", password="pass123")
    u.groups.add(student_group)
    Profile.objects.create(user=u, user_type="STUDENT")
    return u

@pytest.fixture
def section(db, course, semester, room_a, instructor_user):
    s = Section.objects.create(
        course=course, semester=semester, room=room_a, section_number="1", capacity=30
    )
    s.instructors.add(instructor_user)
    return s

# ================================ Helpers ================================
def _login_staff(client, user):
    client.force_login(user)

def _url_ct_add(section):
    return reverse(URL_CT_ADD, args=[section.id])

def _url_ct_edit(ct):
    return reverse(URL_CT_EDIT, args=[ct.id])

def _url_ct_delete(ct):
    return reverse(URL_CT_DELETE, args=[ct.id])

def _payload_add(day, start_hhmm, end_hhmm):
    # ปรับชื่อ key ให้ตรงกับฟอร์มเพิ่มคาบเรียนของคุณ หากต่างจากนี้
    return {"day": day, "start_time": start_hhmm, "end_time": end_hhmm}

# =========================================================
#                    INTEGRATION TESTS
#                  (ตาม TC-078 ถึง TC-087)
# =========================================================

# TC-078: เพิ่มคาบเรียนสำเร็จ
@pytest.mark.django_db
def test_TC_078_add_class_time_success(client, staff_user, section):
    _login_staff(client, staff_user)

    # GET หน้า add (ถ้ามี)
    resp_get = client.get(_url_ct_add(section))
    assert resp_get.status_code in (200, 302, 303)

    # POST เพิ่มคาบ MON 09:00–11:00
    resp = client.post(_url_ct_add(section), _payload_add("MON", "09:00", "11:00"))
    assert resp.status_code in (302, 303)

    assert ClassTime.objects.filter(
        section=section, day="MON", start_time=time(9, 0), end_time=time(11, 0)
    ).exists()

# TC-079: Negative end <= start
@pytest.mark.django_db
def test_TC_079_end_le_start_invalid(client, staff_user, section):
    _login_staff(client, staff_user)

    resp = client.post(_url_ct_add(section), _payload_add("MON", "11:00", "09:00"))
    assert resp.status_code == 200  # ค้างหน้าเดิมเพื่อแสดง error

    assert not ClassTime.objects.filter(section=section, day="MON",
                                        start_time=time(11, 0), end_time=time(9, 0)).exists()

    html = resp.content.decode("utf-8", errors="ignore")
    assert ("เวลาเลิกเรียนต้องอยู่หลังเวลาเริ่มเรียน" in html) or ("end_time" in html)

# TC-080: Negative เวลาทับซ้อนใน Section เดียวกัน
@pytest.mark.django_db
def test_TC_080_overlap_same_section_invalid(client, staff_user, section):
    _login_staff(client, staff_user)
    ClassTime.objects.create(section=section, day="MON", start_time="09:00", end_time="11:00")

    resp = client.post(_url_ct_add(section), _payload_add("MON", "10:00", "12:00"))
    assert resp.status_code == 200

    # ยังมีแค่ตัวเดิม
    assert ClassTime.objects.filter(section=section, day="MON").count() == 1

    html = resp.content.decode("utf-8", errors="ignore")
    assert ("ทับซ้อน" in html) or ("ห้อง" in html) or ("__all__" in html) or ("start_time" in html) or ("end_time" in html)

# TC-081: แก้ไข/ลบคาบเรียน
@pytest.mark.django_db
def test_TC_081_edit_and_delete(client, staff_user, section):
    _login_staff(client, staff_user)
    ct = ClassTime.objects.create(section=section, day="MON", start_time="09:00", end_time="11:00")

    # แก้ไขเป็น 12:00–14:00
    resp_edit = client.post(_url_ct_edit(ct), _payload_add("MON", "12:00", "14:00"))
    assert resp_edit.status_code in (302, 303)

    ct.refresh_from_db()
    assert str(ct.start_time)[:5] == "12:00" and str(ct.end_time)[:5] == "14:00"

    # ลบ
    resp_del = client.post(_url_ct_delete(ct), {})
    assert resp_del.status_code in (302, 303)
    assert not ClassTime.objects.filter(pk=ct.pk).exists()

# TC-082: ลบคาบเรียนที่มีการลงทะเบียน (ลบได้)
@pytest.mark.django_db
def test_TC_082_delete_has_registration(client, staff_user, section, student_user):
    _login_staff(client, staff_user)
    ct = ClassTime.objects.create(section=section, day="MON", start_time="09:00", end_time="11:00")

    # สมมติลงทะเบียนแล้ว
    section.students.add(student_user)

    resp = client.post(_url_ct_delete(ct), {})
    assert resp.status_code in (302, 303)

    with pytest.raises(ClassTime.DoesNotExist):
        ct.refresh_from_db()

# TC-083: Negative ห้องเดียวกัน ต่าง Section เทอมเดียวกัน → ทับซ้อน
@pytest.mark.django_db
def test_TC_083_overlap_same_room_different_section_invalid(client, staff_user, course, semester, room_a, instructor_user):
    _login_staff(client, staff_user)

    s1 = Section.objects.create(course=course, semester=semester, room=room_a, section_number="1", capacity=30)
    s1.instructors.add(instructor_user)
    ClassTime.objects.create(section=s1, day="MON", start_time="09:00", end_time="11:00")

    s2 = Section.objects.create(course=course, semester=semester, room=room_a, section_number="2", capacity=30)
    s2.instructors.add(instructor_user)

    resp = client.post(_url_ct_add(s2), _payload_add("MON", "10:00", "12:00"))
    assert resp.status_code == 200
    assert not ClassTime.objects.filter(section=s2, day="MON").exists()

    html = resp.content.decode("utf-8", errors="ignore")
    assert ("ห้อง" in html and "ถูกใช้งาน" in html) or ("__all__" in html)

# TC-084: Negative อาจารย์คนเดียวกัน ต่างห้อง → ทับซ้อน
@pytest.mark.django_db
def test_TC_084_overlap_same_instructor_invalid(client, staff_user, course, semester, room_a, room_b, instructor_user):
    _login_staff(client, staff_user)

    s1 = Section.objects.create(course=course, semester=semester, room=room_a, section_number="1", capacity=30)
    s1.instructors.add(instructor_user)
    ClassTime.objects.create(section=s1, day="MON", start_time="09:00", end_time="11:00")

    s2 = Section.objects.create(course=course, semester=semester, room=room_b, section_number="2", capacity=30)
    s2.instructors.add(instructor_user)  # อาจารย์ซ้ำ

    resp = client.post(_url_ct_add(s2), _payload_add("MON", "10:00", "12:00"))
    assert resp.status_code == 200
    assert not ClassTime.objects.filter(section=s2, day="MON").exists()

    html = resp.content.decode("utf-8", errors="ignore")
    assert ("ตารางสอนซ้ำซ้อน" in html) or ("__all__" in html)

# TC-085: Negative ชนขอบ 11:00–12:00 ถือว่าทับซ้อน
@pytest.mark.django_db
def test_TC_085_overlap_touching_edges_invalid(client, staff_user, section):
    _login_staff(client, staff_user)
    ClassTime.objects.create(section=section, day="MON", start_time="09:00", end_time="11:00")

    resp = client.post(_url_ct_add(section), _payload_add("MON", "11:00", "12:00"))
    assert resp.status_code == 200
    assert not ClassTime.objects.filter(section=section, day="MON",
                                        start_time=time(11, 0), end_time=time(12, 0)).exists()

    html = resp.content.decode("utf-8", errors="ignore")
    assert ("ทับซ้อน" in html) or ("__all__" in html)

# TC-086: คนละวัน “ไม่ทับซ้อน”
@pytest.mark.django_db
def test_TC_086_different_day_ok(client, staff_user, section):
    _login_staff(client, staff_user)
    ClassTime.objects.create(section=section, day="MON", start_time="09:00", end_time="11:00")

    resp = client.post(_url_ct_add(section), _payload_add("TUE", "09:30", "10:30"))
    assert resp.status_code in (302, 303)

    assert ClassTime.objects.filter(
        section=section, day="TUE", start_time=time(9, 30), end_time=time(10, 30)
    ).exists()

# TC-087: ห้อง/เวลาเดียวกัน แต่คนละเทอม → เพิ่มได้
@pytest.mark.django_db
def test_TC_087_same_room_time_different_semester_ok(client, staff_user, course, semester, semester_next, room_a, instructor_user):
    _login_staff(client, staff_user)

    s1 = Section.objects.create(course=course, semester=semester, room=room_a, section_number="1", capacity=30)
    s1.instructors.add(instructor_user)
    ClassTime.objects.create(section=s1, day="MON", start_time="09:00", end_time="11:00")

    s2 = Section.objects.create(course=course, semester=semester_next, room=room_a, section_number="2", capacity=30)
    s2.instructors.add(instructor_user)

    resp = client.post(_url_ct_add(s2), _payload_add("MON", "09:00", "11:00"))
    assert resp.status_code in (302, 303)

    assert ClassTime.objects.filter(
        section=s2, day="MON", start_time=time(9, 0), end_time=time(11, 0)
    ).exists()
