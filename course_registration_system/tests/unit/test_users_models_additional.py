from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from tests import factories
from users.models import Profile

@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "dob,expect_substring",
    [
        (date.today() + timedelta(days=1), None),
        (date.today() - timedelta(days=14 * 365), "15"),
        (date.today() - timedelta(days=101 * 365), "100"),
    ],
    ids=["future", "too_young", "too_old"],
)
def test_profile_clean_date_of_birth_rules(student, dob, expect_substring):
    # Arrange: ปรับวันเกิดของนักศึกษาให้ผิดเงื่อนไข
    student.date_of_birth = dob

    # Act + Assert: เรียก clean แล้วต้องได้ ValidationError ที่ date_of_birth
    with pytest.raises(ValidationError) as exc:
        student.clean()
    assert "date_of_birth" in exc.value.message_dict
    if expect_substring:
        assert expect_substring in exc.value.message_dict["date_of_birth"][0]

@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name",
    ["student_id", "branch"],
)
def test_profile_clean_student_requires_core_fields(student, field_name):
    # Arrange: ทำให้ข้อมูลนักศึกษาขาด field บังคับ
    setattr(student, field_name, None)

    # Act + Assert: clean ต้องฟ้อง field ที่หาย
    with pytest.raises(ValidationError) as exc:
        student.clean()
    assert field_name in exc.value.message_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_student_rejects_staff_fields(student):
    # Arrange: ใส่ acdemic_title ที่ใช้กับบุคลากร
    student.acdemic_title = Profile.AcademicTitle.LECTURER

    # Act + Assert: ฟังก์ชัน clean ต้องไม่ยอม
    with pytest.raises(ValidationError):
        student.clean()


def _build_instructor_profile():
    """สร้างโปรไฟล์อาจารย์พื้นฐานไว้ใช้ซ้ำ"""
    return Profile(
        user=factories.UserFactory(),
        user_type=Profile.UserType.INSTRUCTOR,
        department=factories.DepartmentFactory(),
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )

@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name",
    ["department", "acdemic_title"],
)
def test_profile_clean_instructor_requires_fields(field_name):
    # Arrange: ตั้งค่าอาจารย์ให้ขาด field ที่จำเป็น
    instructor = _build_instructor_profile()
    setattr(instructor, field_name, None)

    # Act + Assert: clean ต้องบอก field ที่หาย
    with pytest.raises(ValidationError) as exc:
        instructor.clean()
    assert field_name in exc.value.message_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_instructor_rejects_student_fields():
    # Arrange: ใส่ student_id ให้กับอาจารย์
    instructor = _build_instructor_profile()
    instructor.student_id = "66000000"

    # Act + Assert: clean ต้องฟ้องว่าใช้งานไม่ถูกต้อง
    with pytest.raises(ValidationError):
        instructor.clean()


def _build_staff_profile():
    """สร้างโปรไฟล์เจ้าหน้าที่พื้นฐาน"""
    return Profile(
        user=factories.UserFactory(),
        user_type=Profile.UserType.STAFF,
        job_title=Profile.JobTitle.REGISTRATION_OFFICER,
    )

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_staff_requires_job_title():
    # Arrange: ลบ job_title ออกจากเจ้าหน้าที่
    staff = _build_staff_profile()
    staff.job_title = None

    # Act + Assert: ต้องมี error ที่ job_title
    with pytest.raises(ValidationError) as exc:
        staff.clean()
    assert "job_title" in exc.value.message_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_staff_rejects_student_fields():
    # Arrange: ใส่ student_id ให้เจ้าหน้าที่
    staff = _build_staff_profile()
    staff.student_id = "66000001"

    # Act + Assert: clean ต้องไม่ยอม
    with pytest.raises(ValidationError):
        staff.clean()

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_name_fields_must_pair(student):
    # Arrange: ใส่ชื่อแต่ไม่ใส่นามสกุล
    student.last_name_th = ""
    student.first_name_th = "ทดสอบ"

    # Act + Assert: ต้องได้ ValidationError ชวนกรอกให้ครบคู่
    with pytest.raises(ValidationError) as exc:
        student.clean()
    assert any("ชื่อ" in message for message in exc.value.messages)

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_address_min_length(student):
    # Arrange: ใส่ที่อยู่สั้นเกิน 10 ตัวอักษร
    student.address = "123456789"

    # Act + Assert: clean ต้องฟ้องเรื่องความยาว
    with pytest.raises(ValidationError) as exc:
        student.clean()
    assert "address" in exc.value.message_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_str_returns_username_when_no_thai_name():
    # Arrange: สร้างโปรไฟล์ที่ไม่มีชื่อภาษาไทย
    profile = Profile(
        user=factories.UserFactory(username="username123"),
        user_type=Profile.UserType.STAFF,
        job_title=Profile.JobTitle.REGISTRATION_OFFICER,
    )

    # Act: เรียก str(profile)
    rendered = str(profile)

    # Assert: ต้องคืน username
    assert rendered == "username123"

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_get_schedule_filters_by_semester(student):
    semester_current = factories.SemesterFactory()
    # ให้แน่ใจว่า another semester ไม่ซ้ำ (สลับ 1<->2)
    other_sem_value = 1 if getattr(semester_current, "semester", 1) == 2 else 2
    semester_other = factories.SemesterFactory(year=semester_current.year, semester=other_sem_value)

    section_current = factories.SectionFactory(semester=semester_current)
    section_other = factories.SectionFactory(semester=semester_other)
    student.user.enrolled_sections.add(section_current, section_other)

    queryset = student.get_schedule(semester=semester_current)

    assert list(queryset) == [section_current]
