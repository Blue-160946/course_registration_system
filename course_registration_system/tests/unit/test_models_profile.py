from datetime import datetime, timedelta

import pytest
from django.core.exceptions import ValidationError

from users.models import Profile
from payment.models import PaymentTransaction
from tests.factories import (
    BranchFactory,
    CourseFactory,
    SectionFactory,
    StudentFactory,
    SemesterFactory,
)
from tests.conftest import freeze_time as freeze_time_helper

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_student_requires_mandatory_fields():
    """ตรวจว่าโปรไฟล์นักศึกษาต้องมี student_id และ branch"""
    profile = StudentFactory()
    profile.student_id = None

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean()

    assert "student_id" in exc_info.value.error_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_instructor_disallows_student_only_fields():
    """ตรวจว่าโปรไฟล์อาจารย์ห้ามใช้ฟิลด์เฉพาะของนักศึกษา"""
    profile = StudentFactory()
    profile.first_name_th = ""
    profile.last_name_th = ""
    profile.address = "???????????????????????????"
    profile.user_type = Profile.UserType.INSTRUCTOR
    profile.student_status = Profile.StudentStatus.STUDYING
    profile.department = BranchFactory().department
    profile.acdemic_title = Profile.AcademicTitle.LECTURER

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean()

    assert "__all__" in exc_info.value.error_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_staff_requires_job_title():
    """ตรวจว่าโปรไฟล์เจ้าหน้าที่ต้องมี job_title"""
    profile = StudentFactory()
    profile.user_type = Profile.UserType.STAFF
    profile.job_title = None

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean()

    assert "job_title" in str(exc_info.value)

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_clean_rejects_invalid_age():
    """ตรวจว่าอายุของผู้ใช้ต้องไม่ต่ำกว่า 15 ปี"""
    profile = StudentFactory()
    mocked_today = datetime(2024, 1, 1, 0, 0, 0)
    profile.date_of_birth = mocked_today.date() - timedelta(days=10 * 365)

    with freeze_time_helper(mocked_today):
        with pytest.raises(ValidationError) as exc_info:
            profile.full_clean()

    assert "date_of_birth" in exc_info.value.error_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_get_schedule_filters_by_semester():
    """ตรวจว่า get_schedule() คืนค่าเฉพาะเซกชันของภาคเรียนที่ระบุ"""
    profile = StudentFactory()
    section_a = SectionFactory()
    section_b = SectionFactory(semester=SemesterFactory(year=2566))
    profile.user.enrolled_sections.add(section_a, section_b)

    result = profile.get_schedule(section_a.semester)

    assert set(result) == {section_a}

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_get_transcript_returns_success_payments():
    """ตรวจว่า get_transcript() คืนรายการเฉพาะธุรกรรมที่ชำระสำเร็จ (SUCCESS)"""
    profile = StudentFactory()
    course = CourseFactory()
    PaymentTransaction.objects.create(
        student=profile,
        course=course,
        amount=1000,
        status="SUCCESS",
        transaction_id="TXN1",
    )
    PaymentTransaction.objects.create(
        student=profile,
        course=course,
        amount=1000,
        status="FAILED",
    )

    result = profile.get_transcript()

    assert result.count() == 1
    assert all(payment.status == "SUCCESS" for payment in result)
