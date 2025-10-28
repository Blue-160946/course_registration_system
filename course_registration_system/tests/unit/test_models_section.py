from datetime import time

import pytest
from django.core.exceptions import ValidationError

from courses.models import ClassTime, Section
from tests.factories import (
    CourseFactory,
    SectionFactory,
    StudentFactory,
    SemesterFactory,
    RoomFactory,
)

@pytest.mark.unit
@pytest.mark.django_db
def test_section_available_seats_updates_after_enrollment():
    """ตรวจว่า available_seats ถูกอัปเดตหลังเพิ่มนักศึกษา และ is_full() ทำงานถูกต้อง"""
    section = SectionFactory(capacity=2)
    student_a = StudentFactory()
    student_b = StudentFactory()

    section.students.add(student_a.user)
    assert section.available_seats == 1

    section.students.add(student_b.user)
    assert section.available_seats == 0
    assert section.is_full() is True

@pytest.mark.unit
@pytest.mark.django_db
def test_section_str_shows_course_and_section_number():
    """ตรวจว่า __str__ แสดงรหัสวิชาและเลขเซกชัน"""
    section = SectionFactory(section_number="5")
    result = str(section)

    assert section.course.code in result
    assert "5" in result

@pytest.mark.unit
@pytest.mark.django_db
def test_section_clean_rejects_over_capacity():
    """ตรวจว่า clean() ปฏิเสธกรณีจำนวนนักศึกษาเกินความจุของเซกชัน"""
    section = SectionFactory(capacity=1)
    student_a = StudentFactory()
    student_b = StudentFactory()
    section.students.add(student_a.user)
    section.students.add(student_b.user)

    with pytest.raises(ValidationError) as exc_info:
        section.clean()

    assert exc_info.value.messages

@pytest.mark.unit
@pytest.mark.django_db
def test_section_clean_detects_room_overlap(monkeypatch):
    """ตรวจว่า clean() จับชนเวลาสอนห้องเดียวกันในภาคเรียนเดียวกันได้ (room overlap)"""
    semester = SemesterFactory()
    room = RoomFactory()
    course = CourseFactory()
    section_a = SectionFactory(course=course, semester=semester, room=room)
    ClassTime.objects.create(
        section=section_a,
        day="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    section_b = SectionFactory(course=course, semester=semester, room=room)
    ClassTime.objects.create(
        section=section_b,
        day="MON",
        start_time=time(9, 30),
        end_time=time(10, 30),
    )
    section_b.classtime_set = section_b.class_times.all()

    section_a_classtime = section_a.class_times.all()
    dummy_section = Section.objects.get(pk=section_a.pk)
    dummy_section.classtime_set = section_a_classtime

    class DummyQuerySet(list):
        def exclude(self, **kwargs):
            return self

    monkeypatch.setattr(
        Section.objects,
        "filter",
        lambda **kwargs: DummyQuerySet([dummy_section]),
    )

    with pytest.raises(ValidationError) as exc_info:
        section_b.clean()

    assert exc_info.value.messages or "room" in str(exc_info.value)
