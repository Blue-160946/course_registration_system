from datetime import time

import pytest
from django.core.exceptions import ValidationError

from courses.models import ClassTime
from tests.factories import SectionFactory, StudentFactory

@pytest.mark.unit
@pytest.mark.django_db
def test_classtime_clean_accepts_valid_range():
    """ตรวจว่าระยะเวลา 2 ชั่วโมงพอดีถือว่าถูกต้อง"""
    # Arrange
    section = SectionFactory()
    classtime = ClassTime(
        section=section,
        day="MON",
        start_time=time(9, 0),
        end_time=time(11, 0),
    )

    # Act / Assert
    classtime.full_clean()

@pytest.mark.unit
@pytest.mark.django_db
def test_classtime_str_contains_course_and_day():
    """ตรวจว่า __str__ แสดงรหัสวิชาและวัน"""
    # Arrange
    section = SectionFactory()
    classtime = ClassTime.objects.create(
        section=section,
        day="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    # Act
    result = str(classtime)

    # Assert
    assert section.course.code in result
    assert classtime.get_day_display() in result

@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_time_value,end_time_value,expected_message",
    [
        pytest.param(time(10, 0), time(9, 0), "end_time", id="end_before_start"),
        pytest.param(time(9, 0), time(12, 5), "2", id="duration_over_two_hours"),
    ],
)
def test_classtime_clean_rejects_time_range(start_time_value, end_time_value, expected_message):
    """ตรวจว่าช่วงเวลาที่ผิดต้องถูกปฏิเสธ"""
    # Arrange
    section = SectionFactory()
    classtime = ClassTime(
        section=section,
        day="MON",
        start_time=start_time_value,
        end_time=end_time_value,
    )

    # Act / Assert
    with pytest.raises(ValidationError) as exc_info:
        classtime.full_clean()

    # Assert
    assert expected_message in str(exc_info.value)

@pytest.mark.unit
@pytest.mark.django_db
def test_classtime_clean_rejects_overlap_with_same_room_and_instructor():
    """ตรวจว่าช่วงเวลาซ้อนกับอาจารย์/ห้องเดิมต้องถูกยกเลิก"""
    # Arrange
    section_a = SectionFactory()
    instructor = StudentFactory().user  # reuse user เป็นผู้สอนจำลอง
    section_a.instructors.add(instructor)
    ClassTime.objects.create(
        section=section_a,
        day="TUE",
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    section_b = SectionFactory(room=section_a.room, semester=section_a.semester)
    section_b.instructors.add(instructor)
    classtime = ClassTime(
        section=section_b,
        day="TUE",
        start_time=time(9, 30),
        end_time=time(10, 30),
    )

    # Act / Assert
    with pytest.raises(ValidationError) as exc_info:
        classtime.full_clean()

    # Assert
    assert exc_info.value.messages  # มีข้อความแจ้งเตือนจริง
