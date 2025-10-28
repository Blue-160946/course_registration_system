import pytest
from django.contrib import admin

from courses.admin import SectionAdmin
from courses.models import ClassTime
from tests.factories import (
    SectionFactory,
    StudentFactory,
)
from users.models import Profile


def _make_instructor_with_names():
    profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        department=SectionFactory().course.department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    profile.first_name_th = "กิตติ"
    profile.last_name_th = "เทส"
    profile.address = "ที่อยู่การสอน"
    profile.save()
    return profile.user

@pytest.mark.unit
@pytest.mark.django_db
def test_section_admin_display_instructors_handles_names():
    """ตรวจข้อความรายชื่อผู้สอนใน admin"""
    section = SectionFactory()
    instructor = _make_instructor_with_names()
    section.instructors.add(instructor)
    admin_view = SectionAdmin(SectionFactory._meta.model, admin.site)

    label = admin_view.display_instructors(section)

    assert "กิตติ" in label

@pytest.mark.unit
@pytest.mark.django_db
def test_section_admin_display_class_times_formats_schedule():
    """ตรวจข้อความตารางสอนใน admin"""
    section = SectionFactory()
    ClassTime.objects.create(
        section=section,
        day="MON",
        start_time="09:00",
        end_time="10:00",
    )
    admin_view = SectionAdmin(SectionFactory._meta.model, admin.site)

    rendered = admin_view.display_class_times(section)

    assert "MON" in rendered or "จันทร์" in rendered

@pytest.mark.unit
@pytest.mark.django_db
def test_section_admin_display_instructors_fallback_username():
    """ตรวจว่า display_instructors() ใช้ username แทนเมื่อไม่มีชื่อจริงของผู้สอน"""
    section = SectionFactory()
    profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        department=section.course.department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    profile.first_name_th = ""
    profile.last_name_th = ""
    profile.address = "???????????????????????????"
    profile.save()
    section.instructors.add(profile.user)
    admin_view = SectionAdmin(SectionFactory._meta.model, admin.site)

    label = admin_view.display_instructors(section)

    assert profile.user.username in label

