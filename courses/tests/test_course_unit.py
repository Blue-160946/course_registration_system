import pytest
from datetime import date
from django.core.exceptions import ValidationError

from courses.models import Faculty, Department, Course, Semester, Room, Section

# =============== Fixtures ขั้นต่ำ ===============
@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="วิทยาศาสตร์")

@pytest.fixture
def department(db, faculty):
    return Department.objects.create(name="คอมพิวเตอร์", faculty=faculty)

# =============== โมเดล: Course ===============

# UT-CRS-001: โมเดลสร้างได้เมื่อข้อมูลถูกต้อง
@pytest.mark.django_db
def test_UT_CRS_001_course_model_create_valid(department):
    c = Course(code="123456", name="Programming", department=department, credits=3, is_active=True)
    c.full_clean() # ตรวจสอบความถูกต้อง
    c.save()
    assert Course.objects.filter(pk=c.pk).exists()

# UT-CRS-002: code ต้องไม่ซ้ำ (unique)
@pytest.mark.django_db
def test_UT_CRS_002_course_model_code_unique(department):
    Course.objects.create(code="123456", name="A", department=department, credits=3, is_active=True)
    dup = Course(code="123456", name="B", department=department, credits=4, is_active=True)
    with pytest.raises(ValidationError):
        dup.full_clean()

# UT-CRS-003: ต้องมี department (ห้ามเว้นว่าง)
@pytest.mark.django_db
def test_UT_CRS_003_course_model_department_required(department):
    c = Course(code="234567", name="Algo", department=None, credits=3, is_active=True)
    with pytest.raises(ValidationError) as e:
        c.full_clean()
    assert "department" in e.value.message_dict

# UT-CRS-004: อัปเดต code ไปชนของคนอื่น → ไม่อนุญาต
@pytest.mark.django_db
def test_UT_CRS_004_course_model_update_code_to_existing_blocked(department):
    a = Course.objects.create(code="111111", name="A", department=department, credits=3, is_active=True)
    b = Course.objects.create(code="222222", name="B", department=department, credits=3, is_active=True)
    b.code = "111111"
    with pytest.raises(ValidationError):
        b.full_clean()

# =============== ฟอร์ม: CourseForm (ถ้ามี) ===============

def _require_course_form():
    try:
        from courses.forms import CourseForm
    except Exception:
        pytest.skip("ไม่มี CourseForm ให้ทดสอบ")
    return CourseForm

def _form_payload(department, **overrides):
    data = {
        "code": "123456",
        "name": "Programming",
        "department": department.id,
        "credits": 3,
        "is_active": True,
    }
    data.update(overrides)
    return data

# UT-CRS-005: ฟอร์ม valid เมื่อข้อมูลถูกต้อง
@pytest.mark.django_db
def test_UT_CRS_005_course_form_valid(department):
    CourseForm = _require_course_form()
    form = CourseForm(data=_form_payload(department))
    assert form.is_valid(), form.errors
    obj = form.save()
    assert Course.objects.filter(pk=obj.pk, code="123456").exists()

# UT-CRS-006: code ต้องเป็น “ตัวเลข 6 หลัก” (เช็คฟอร์ม)
@pytest.mark.django_db
@pytest.mark.parametrize("bad_code", ["ABC123", "12345", "1234567", "12 456", "12-456"])
def test_UT_CRS_006_course_form_code_format_invalid(department, bad_code):
    CourseForm = _require_course_form()
    form = CourseForm(data=_form_payload(department, code=bad_code))
    assert not form.is_valid()
    assert "code" in form.errors  # ฟอร์มควรฟ้อง field code

# UT-CRS-007: credits ต้องเป็นตัวเลขบวก (เช็คฟอร์ม)
@pytest.mark.django_db
@pytest.mark.parametrize("bad_credits", [0, -1, "abc"])
def test_UT_CRS_007_course_form_credits_invalid(department, bad_credits):
    CourseForm = _require_course_form()
    form = CourseForm(data=_form_payload(department, credits=bad_credits))
    assert not form.is_valid()
    assert "credits" in form.errors

# UT-CRS-008: ไม่เลือก department → ฟอร์มต้องฟ้อง
@pytest.mark.django_db
def test_UT_CRS_008_course_form_department_required(department):
    try:
        from courses.forms import CourseForm
    except Exception:
        pytest.skip("ไม่มี CourseForm ให้ทดสอบ")

    form = CourseForm(data={
        "code": "123456",
        "name": "Programming",
        "department": "",   # ไม่เลือก
        "credits": 3,
        "is_active": True,
    })
    assert not form.is_valid()
    assert "department" in form.errors

# UT-CRS-009: เปลี่ยนชื่อวิชา/เครดิตได้ตามปกติ (ฟอร์ม)
@pytest.mark.django_db
def test_UT_CRS_009_course_form_update_fields_ok(department):
    # สร้างก่อน
    c = Course.objects.create(code="345678", name="Old", department=department, credits=2, is_active=True)

    CourseForm = _require_course_form()
    form = CourseForm(
        data=_form_payload(department, code="345678", name="NewName", credits=4),
        instance=c,
    )
    assert form.is_valid(), form.errors
    updated = form.save()
    assert updated.name == "NewName" and updated.credits == 4

# UT-CRS-010: ฟอร์มป้องกัน code ซ้ำ (ตอนแก้ไข)
@pytest.mark.django_db
def test_UT_CRS_010_course_form_update_code_to_duplicate_blocked(department):
    a = Course.objects.create(code="555555", name="A", department=department, credits=3, is_active=True)
    b = Course.objects.create(code="666666", name="B", department=department, credits=3, is_active=True)

    CourseForm = _require_course_form()
    form = CourseForm(
        data=_form_payload(department, code="555555", name="B-new"),
        instance=b,
    )
    assert not form.is_valid()
    assert "code" in form.errors
