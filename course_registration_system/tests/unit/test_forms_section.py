import pytest

from courses.forms import SectionForm
from tests.factories import (
    CourseFactory,
    SectionFactory,
    SemesterFactory,
    RoomFactory,
    StudentFactory,
)

@pytest.mark.unit
@pytest.mark.django_db
def test_section_form_valid_when_section_number_unique():
    """ตรวจว่าเลขเซกชันไม่ซ้ำผ่านฟอร์มได้"""
    # Arrange
    course = CourseFactory()
    semester = SemesterFactory()
    room = RoomFactory()
    instructor_profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        acdemic_title=Profile.AcademicTitle.LECTURER,
        department=course.department,
    )
    instructor = instructor_profile.user
    data = {
        "semester": semester.pk,
        "section_number": "1",
        "room": room.pk,
        "capacity": 40,
        "instructors": [instructor.pk],
    }

    # Act
    form = SectionForm(data=data, course=course)

    # Assert
    assert form.is_valid()

@pytest.mark.unit
@pytest.mark.django_db
def test_section_form_rejects_duplicate_section_number():
    """ตรวจว่าห้ามเลขเซกชันซ้ำในวิชา+ภาคเรียนเดียวกัน"""
    # Arrange
    existing = SectionFactory(section_number="1")
    instructor_profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        acdemic_title=Profile.AcademicTitle.LECTURER,
        department=existing.course.department,
    )
    instructor = instructor_profile.user
    data = {
        "semester": existing.semester.pk,
        "section_number": "1",
        "room": existing.room.pk,
        "capacity": 30,
        "instructors": [instructor.pk],
    }

    # Act
    form = SectionForm(data=data, course=existing.course)

    # Assert
    assert form.is_valid() is False
    assert "section_number" in form.errors  # ต้องมีข้อความเตือนภาษาไทย

@pytest.mark.unit
@pytest.mark.django_db
def test_section_form_allows_update_same_section_number():
    """ตรวจว่าการแก้ไขเซกชันเดิมไม่ควรถูกแจ้งซ้ำ"""
    # Arrange
    section = SectionFactory(section_number="2")
    instructor_profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        acdemic_title=Profile.AcademicTitle.LECTURER,
        department=section.course.department,
    )
    instructor = instructor_profile.user
    data = {
        "semester": section.semester.pk,
        "section_number": "2",
        "room": section.room.pk,
        "capacity": 35,
        "instructors": [instructor.pk],
    }

    # Act
    form = SectionForm(data=data, course=section.course, instance=section)

    # Assert
    assert form.is_valid()
from users.models import Profile
