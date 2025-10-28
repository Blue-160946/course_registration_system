import pytest
from datetime import time

from django import forms

from courses.forms import ClassTimeForm, SectionForm
from courses.models import ClassTime
from tests import factories
from users.models import Profile


def _create_instructor(department):
    """Helper เพื่อสร้างอาจารย์สำหรับเทส"""
    instructor_user = factories.UserFactory()
    Profile.objects.create(
        user=instructor_user,
        user_type=Profile.UserType.INSTRUCTOR,
        department=department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    return instructor_user

@pytest.mark.unit
@pytest.mark.django_db
def test_section_form_widget_respects_checkbox(monkeypatch):
    # Arrange: เตรียมฟอร์มที่ปรับ widget เป็น CheckboxSelectMultiple
    course = factories.CourseFactory()
    monkeypatch.setattr(
        SectionForm.base_fields["instructors"],
        "widget",
        forms.CheckboxSelectMultiple(),
        raising=False,
    )

    # Act: สร้างฟอร์มโดยส่ง course เพื่อกระตุ้น __init__
    form = SectionForm(course=course)

    # Assert: ตรวจสอบว่า field ปกติถูกเติม class และ checkbox ไม่ถูกแตะ
    assert form.fields["capacity"].widget.attrs["class"] == "form-control"
    assert "class" not in form.fields["instructors"].widget.attrs

@pytest.mark.unit
@pytest.mark.django_db
def test_section_form_detects_duplicate_section_number():
    # Arrange: สร้าง Section เดิมและข้อมูล POST ชนกัน
    course = factories.CourseFactory()
    existing_section = factories.SectionFactory(course=course, section_number="1")
    instructor = _create_instructor(course.department)
    payload = {
        "semester": existing_section.semester.pk,
        "section_number": existing_section.section_number,
        "room": existing_section.room.pk,
        "capacity": existing_section.capacity,
        "instructors": [instructor.pk],
    }

    # Act: เรียก form.is_valid() ด้วยข้อมูลซ้ำ
    form = SectionForm(data=payload, course=course)

    # Assert: ฟอร์มต้อง invalid และแจ้ง error ที่ section_number
    assert not form.is_valid()
    assert "section_number" in form.errors
    assert any("Sec" in message for message in form.errors["section_number"])

@pytest.mark.unit
@pytest.mark.django_db
def test_class_time_form_flags_boundary_overlap_and_instructor_conflict():
    # Arrange: ตั้ง Section ที่มีเวลาเรียนเดิมและอาจารย์ร่วม
    section = factories.SectionFactory()
    instructor = _create_instructor(section.course.department)
    section.instructors.add(instructor)
    ClassTime.objects.create(
        section=section,
        day="MON",
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    payload = {
        "day": "MON",
        "start_time": "10:00",
        "end_time": "11:00",
    }

    # Act: ส่งข้อมูลที่ชนขอบเวลาและอาจารย์คนเดิม
    form = ClassTimeForm(data=payload, section=section)

    # Assert: ตรวจสอบว่าฟอร์มมี non field error ทั้งเรื่องชนขอบและอาจารย์
    assert not form.is_valid()
    errors = form.non_field_errors()
    assert any("ชนขอบ" in message for message in errors)
    assert any("อาจารย์" in message for message in errors)
