import pytest
from hypothesis import assume, given, strategies as st, settings

from courses.forms import ClassTimeForm, SectionForm
from tests.factories import (
    CourseFactory,
    RoomFactory,
    SectionFactory,
    SemesterFactory,
    StudentFactory,
)
from users.models import Profile


def minutes_to_str(total_minutes: int) -> str:
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"


@st.composite
def valid_time_ranges(draw):
    """สร้างช่วงเวลาที่ความยาวไม่เกิน 2 ชั่วโมงและเริ่มก่อนจบ"""
    start_minutes = draw(st.integers(min_value=8 * 60, max_value=(23 * 60) - 120))
    duration = draw(st.integers(min_value=1, max_value=120))
    end_minutes = start_minutes + duration
    assume(end_minutes > start_minutes)
    assume(end_minutes <= 23 * 60 + 59)
    return minutes_to_str(start_minutes), minutes_to_str(end_minutes)


@st.composite
def invalid_time_ranges(draw):
    """สร้างช่วงเวลาที่ผิดหลัก (จบก่อน/เท่ากับเริ่ม หรือยาวเกิน 2 ชั่วโมง)"""
    mode = draw(st.sampled_from(["non_positive", "too_long"]))
    if mode == "non_positive":
        diff = draw(st.integers(min_value=1, max_value=120))
        start_minutes = draw(st.integers(min_value=diff, max_value=22 * 60))
        end_minutes = start_minutes - diff
    else:
        start_minutes = draw(st.integers(min_value=8 * 60, max_value=21 * 60))
        duration = draw(st.integers(min_value=121, max_value=240))
        end_minutes = start_minutes + duration
        assume(end_minutes <= 23 * 60 + 59)
    return minutes_to_str(start_minutes), minutes_to_str(end_minutes)


def build_instructor_for_course(course):
    """สร้างโปรไฟล์อาจารย์ให้เลือกในฟอร์ม"""
    profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        acdemic_title=Profile.AcademicTitle.LECTURER,
        department=course.department,
    )
    return profile.user

@pytest.mark.unit
@settings(deadline=None)
@pytest.mark.django_db
@given(valid_time_ranges())
def test_classtime_form_property_accepts_valid_ranges(time_pair):
    """property: เมื่อเวลาเริ่มก่อนจบและระยะ ≤ 2 ชั่วโมง ฟอร์มต้อง valid"""
    # Arrange
    start_str, end_str = time_pair
    section = SectionFactory()
    data = {"day": "MON", "start_time": start_str, "end_time": end_str}

    # Act
    form = ClassTimeForm(data=data, section=section)

    # Assert
    assert form.is_valid()

@pytest.mark.unit
@settings(deadline=None)
@pytest.mark.django_db
@given(invalid_time_ranges())
def test_classtime_form_property_rejects_invalid_ranges(time_pair):
    """property: เมื่อช่วงเวลาไม่เป็นไปตามกติกา ฟอร์มต้อง invalid"""
    # Arrange
    start_str, end_str = time_pair
    section = SectionFactory()
    data = {"day": "MON", "start_time": start_str, "end_time": end_str}

    # Act
    form = ClassTimeForm(data=data, section=section)

    # Assert
    assert not form.is_valid()

@pytest.mark.unit
@settings(deadline=None)
@pytest.mark.django_db
@given(
    section_number=st.integers(min_value=1, max_value=99),
    capacity=st.integers(min_value=1, max_value=200),
)
def test_section_form_property_valid_when_unique(section_number, capacity):
    """property: ถ้าเลขเซกชันยังไม่ถูกใช้ในภาคเรียนเดียวกัน ฟอร์มต้อง valid"""
    # Arrange
    course = CourseFactory()
    semester = SemesterFactory()
    room = RoomFactory()
    instructor_user = build_instructor_for_course(course)
    data = {
        "semester": semester.pk,
        "section_number": str(section_number),
        "room": room.pk,
        "capacity": capacity,
        "instructors": [instructor_user.pk],
    }

    # Act
    form = SectionForm(data=data, course=course)

    # Assert
    assert form.is_valid()

@pytest.mark.unit
@settings(deadline=None)
@pytest.mark.django_db
@given(section_number=st.integers(min_value=1, max_value=99))
def test_section_form_property_rejects_duplicate_number(section_number):
    """property: ถ้าเลขเซกชันถูกใช้แล้วในวิชา/ภาคเรียนเดียวกัน ต้อง invalid"""
    # Arrange
    course = CourseFactory()
    semester = SemesterFactory()
    room = RoomFactory()
    instructor_user = build_instructor_for_course(course)
    existing = SectionFactory(
        course=course,
        semester=semester,
        section_number=str(section_number),
        room=room,
    )

    data = {
        "semester": semester.pk,
        "section_number": str(section_number),
        "room": room.pk,
        "capacity": existing.capacity,
        "instructors": [instructor_user.pk],
    }

    # Act
    form = SectionForm(data=data, course=course)

    # Assert
    assert not form.is_valid()
