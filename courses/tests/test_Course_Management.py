import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group

from courses.forms import SectionForm, ClassTimeForm  
from courses.models import Course, Section, Room, Semester, Department, Faculty

# พยายาม import Profile จากแอป users ก่อน ถ้าไม่มีค่อย fallback ไปที่ courses
try:
    from users.models import Profile
except Exception:
    from courses.models import Profile

from datetime import date

# --------------------
# Fixtures: ข้อมูลอ้างอิง
# --------------------
@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="วิทยาศาสตร์")

@pytest.fixture
def department(db, faculty):
    return Department.objects.create(name="คอมพิวเตอร์", faculty=faculty)

@pytest.fixture
def course(db, department):
    return Course.objects.create(
        code="CS101", name="Programming",
        department=department, credits=3, description="Intro", is_active=True
    )

@pytest.fixture
def semester(db):
    return Semester.objects.create(
        year=2567, semester=1,
        start_date=date(2025, 6, 1),
        end_date=date(2025, 10, 1),
    )

@pytest.fixture
def room(db):
    return Room.objects.create(building="A", room_number="101")

# --------------------
# Fixtures: Groups
# --------------------
@pytest.fixture
def staff_group(db):
    return Group.objects.get_or_create(name="staff")[0]

@pytest.fixture
def instructor_group(db):
    return Group.objects.get_or_create(name="instructor")[0]

@pytest.fixture
def student_group(db):
    return Group.objects.get_or_create(name="student")[0]

# --------------------
# Fixtures: Users (+ Profile.user_type)
# --------------------
@pytest.fixture
def staff_user(db, staff_group):
    user = User.objects.create_user(
        username="admin", password="123456789", is_staff=True
    )
    user.groups.add(staff_group)
    Profile.objects.create(user=user, user_type="ADMIN")
    return user

@pytest.fixture
def instructor_user(db, instructor_group):
    user = User.objects.create_user(username="instructor", password="pass123")
    user.groups.add(instructor_group)
    Profile.objects.create(user=user, user_type="INSTRUCTOR",
                           first_name_th="สมชาย", last_name_th="ใจดี")
    return user

@pytest.fixture
def student_user(db, student_group):
    user = User.objects.create_user(username="student", password="pass123")
    user.groups.add(student_group)
    Profile.objects.create(user=user, user_type="STUDENT")
    return user

# --------------------
# Fixtures: Section พร้อมอาจารย์
# --------------------
@pytest.fixture
def section(db, course, semester, room, instructor_user):
    s = Section.objects.create(
        course=course,
        section_number="1",
        semester=semester,
        room=room,
        capacity=30,
    )
    s.instructors.add(instructor_user)
    return s

# -----------------------------
# URL name constants 
# -----------------------------
URL_COURSE_ADD = "courses:course-add"
URL_COURSE_EDIT = "courses:course-edit"
URL_COURSE_LIST  = "courses:course-list" 
URL_COURSE_DELETE = "courses:course-delete"

URL_SECTION_LIST = "courses:section-list"     # args=[course.id]
URL_SECTION_ADD = "courses:section-add"       # args=[course.id]
URL_SECTION_EDIT = "courses:section-edit"     # args=[section.id]
URL_SECTION_DELETE = "courses:section-delete" # args=[section.id]

# -----------------------------
# Helpers
# -----------------------------
def _login_staff(client, staff_user):
    client.force_login(staff_user)

def _get_add_course_payload(dept, **overrides):
    base = dict(
        code="123456",
        name="Programming",
        credits=3,
        department=dept.id,
        description="Intro",
        is_active=True,
    )
    base.update(overrides)
    return base

def _post_course_add(client, dept, **overrides):
    url = reverse(URL_COURSE_ADD)
    return client.post(url, _get_add_course_payload(dept, **overrides))

def _post_course_edit(client, obj, **overrides):
    url = reverse(URL_COURSE_EDIT, args=[obj.id])
    payload = _get_add_course_payload(
        obj.department,
        code=obj.code,
        name=obj.name,
        credits=obj.credits,
         description=(getattr(obj, "description", "") or ""),
        is_active=getattr(obj, "is_active", True),
    )
    payload.update(overrides)
    return client.post(url, payload)

def _get_add_section_payload(semester, room, instructor_user, **overrides):
    base = dict(
        semester=semester.id,
        section_number="1",
        room=room.id,
        capacity=30,
        instructors=[str(instructor_user.id)] if instructor_user else [],
        # formset management fields
        **{
            "class_times-TOTAL_FORMS": 0,
            "class_times-INITIAL_FORMS": 0,
            "class_times-MIN_NUM_FORMS": 0,
            "class_times-MAX_NUM_FORMS": 1000,
        }
    )
    base.update(overrides)
    return base

def _post_section_add(client, course, semester, room, instructor_user, **overrides):
    url = reverse(URL_SECTION_ADD, args=[course.id])
    return client.post(url, _get_add_section_payload(semester, room, instructor_user, **overrides))

def _post_section_edit(client, section: Section, **overrides):
    url = reverse(URL_SECTION_EDIT, args=[section.id])
    payload = _get_add_section_payload(
        section.semester,
        section.room,
        None,
        section_number=section.section_number,
        capacity=section.capacity,
        instructors=[str(u.id) for u in section.instructors.all()],
    )
    payload.update(overrides)
    return client.post(url, payload)

# =========================================================
#                  COURSE TESTS  (CRS-xxx)
# =========================================================

# CRS-001: Add form แสดงฟิลด์ครบ
@pytest.mark.django_db
def test_CRS_001_course_add_form_fields_present(client, staff_user):
    _login_staff(client, staff_user)
    resp = client.get(reverse(URL_COURSE_ADD))
    assert resp.status_code == 200
    # ถ้ามี form ใน context ใช้ตรวจชื่อฟิลด์, ไม่งั้นเช็คข้อความใน HTML
    if hasattr(resp, "context") and resp.context and "form" in resp.context:
        form = resp.context["form"]
        expected = {"code","name","credits","department","description","is_active"}
        assert expected.issubset(set(form.fields.keys()))
    else:
        html = resp.content.decode("utf-8")
        for text in ["Course Code","Course Name","Credits","Department","Description","Active","Save","Cancel"]:
            assert text in html

# CRS-002: create course (สถานะ=True)
@pytest.mark.django_db
def test_CRS_002_course_add_success_active_true(client, staff_user, department):
    _login_staff(client, staff_user)
    resp = _post_course_add(client, department, is_active=True)
    assert resp.status_code in (302, 303)
    obj = Course.objects.get(code="123456")
    assert obj.is_active is True

# CRS-003: create course (สถานะ=False)
@pytest.mark.django_db
def test_CRS_003_course_add_success_inactive(client, staff_user, department):
    _login_staff(client, staff_user)
    resp = _post_course_add(client, department, is_active=False)
    assert resp.status_code in (302, 303)
    obj = Course.objects.get(code="123456")
    assert obj.is_active is False

# CRS-004: invalid code
@pytest.mark.django_db
@pytest.mark.parametrize("bad_code", ["", "   ", "CS-101", "101CS", "cs101"])
def test_CRS_004_course_add_invalid_code(client, staff_user, department, bad_code):
    _login_staff(client, staff_user)
    resp = _post_course_add(client, department, code=bad_code)
    assert resp.status_code == 200
    assert "code" in resp.context["form"].errors

# CRS-005: duplicate code
@pytest.mark.django_db
def test_CRS_005_course_add_duplicate_code(client, staff_user, department):
    _login_staff(client, staff_user)
    Course.objects.create(code="CS101", name="Old", department=department, credits=3)
    resp = _post_course_add(client, department, code="CS101")
    assert resp.status_code == 200
    assert "code" in resp.context["form"].errors

# CRS-006: invalid name
@pytest.mark.django_db
@pytest.mark.parametrize("bad_name", ["", "   ", "X"*256])
def test_CRS_006_course_add_invalid_name(client, staff_user, department, bad_name):
    _login_staff(client, staff_user)
    resp = _post_course_add(client, department, name=bad_name)
    assert resp.status_code == 200
    assert "name" in resp.context["form"].errors

# CRS-007: invalid credits
@pytest.mark.django_db
@pytest.mark.parametrize("bad_credits", [0, -1, 1.5, "abc"])
def test_CRS_007_course_add_invalid_credits(client, staff_user, department, bad_credits):
    _login_staff(client, staff_user)
    resp = _post_course_add(client, department, credits=bad_credits)
    assert resp.status_code == 200
    assert "credits" in resp.context["form"].errors

# CRS-008: invalid department
@pytest.mark.django_db
@pytest.mark.parametrize("bad_dep", ["", 999999])
def test_CRS_008_course_add_invalid_department(client, staff_user, department, bad_dep):
    _login_staff(client, staff_user)
    resp = _post_course_add(client, department, department=bad_dep)
    assert resp.status_code == 200
    # assert "department" in resp.context["form"].errors

# CRS-009: blank description allowed (if optional)
@pytest.mark.django_db
def test_CRS_009_course_add_blank_description_ok(client, staff_user, department):
    _login_staff(client, staff_user)
    resp = _post_course_add(client, department, description="")
    assert resp.status_code in (302, 303)
    assert Course.objects.filter(code="123456").exists()

# CRS-010: cancel add → no create
@pytest.mark.django_db
def test_CRS_010_course_add_cancel_no_create(client, staff_user):
    _login_staff(client, staff_user)

    # เปิดหน้าเพิ่มรายวิชา (GET) – ฟอร์มว่าง
    resp = client.get(reverse(URL_COURSE_ADD))
    assert resp.status_code == 200
    before = Course.objects.count()

    # จำลอง "กดลิงก์ยกเลิก" ด้วยการ GET ไปหน้ารายการ
    resp = client.get(reverse(URL_COURSE_LIST))
    assert resp.status_code == 200

    # ต้องไม่เกิดการสร้างข้อมูลใหม่
    assert Course.objects.count() == before

# CRS-011: edit success
@pytest.mark.django_db
def test_CRS_011_course_edit_success(client, staff_user, department):
    _login_staff(client, staff_user)
    obj = Course.objects.create(code="123456", name="Programming", department=department, credits=3, description="Intro", is_active=True)
    resp = _post_course_edit(client, obj, name="Programming I")
    assert resp.status_code in (302, 303)
    obj.refresh_from_db()
    assert obj.name == "Programming I"

# CRS-012: edit to duplicate code
@pytest.mark.django_db
def test_CRS_012_course_edit_to_duplicate_code(client, staff_user, department):
    _login_staff(client, staff_user)
    a = Course.objects.create(code="123456", name="A", department=department, credits=3)
    b = Course.objects.create(code="CS102", name="B", department=department, credits=3)
    resp = _post_course_edit(client, b, code="CS101")
    assert resp.status_code == 200
    assert "code" in resp.context["form"].errors

# CRS-013A: cancel via link (GET) → should NOT delete
@pytest.mark.django_db
def test_CRS_013A_course_delete_cancel_via_link_no_delete(client, staff_user, department):
    _login_staff(client, staff_user)
    obj = Course.objects.create(code="123456", name="A", department=department, credits=3)

    # เปิดหน้า confirm delete
    resp = client.get(reverse(URL_COURSE_DELETE, args=[obj.id]))
    assert resp.status_code == 200

    before = Course.objects.count()

    # จำลอง "กดลิงก์ยกเลิก" (GET ไปหน้ารายการ)
    resp = client.get(reverse(URL_COURSE_LIST))
    assert resp.status_code == 200

    # ไม่ควรถูกลบ
    assert Course.objects.filter(id=obj.id).exists()
    assert Course.objects.count() == before


# CRS-013B: confirm delete (POST) → should delete and redirect
@pytest.mark.django_db
def test_CRS_013B_course_delete_confirm_post_deletes(client, staff_user, department):
    _login_staff(client, staff_user)
    obj = Course.objects.create(code="123456", name="A", department=department, credits=3)
    url = reverse(URL_COURSE_DELETE, args=[obj.id])

    # กดลบ (POST โดยไม่ต้องส่ง cancel)
    resp = client.post(url, {})
    assert resp.status_code in (302, 303)

    # ต้องถูกลบจริง
    assert not Course.objects.filter(id=obj.id).exists()


