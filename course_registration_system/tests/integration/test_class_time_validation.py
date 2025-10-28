from datetime import time

import pytest
from django.urls import reverse

from courses.models import ClassTime
from tests import factories
from users.models import Profile


@pytest.mark.integration
@pytest.mark.django_db
def test_time_add_rejects_end_before_start(client, admin_user):
    # Arrange: เตรียม section และล็อกอิน staff
    section = factories.SectionFactory()
    client.force_login(admin_user)

    # Act: ส่งข้อมูลเวลาสิ้นสุดก่อนเวลาเริ่ม
    response = client.post(
        reverse("courses:time-add", args=[section.pk]),
        data={"day": "MON", "start_time": "10:00", "end_time": "09:00"},
    )

    # Assert: ฟอร์มแจ้งข้อผิดพลาดและไม่สร้าง ClassTime
    form = response.context["form"]
    assert "end_time" in form.errors
    assert ClassTime.objects.filter(section=section).count() == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_time_add_rejects_duration_over_two_hours(client, admin_user):
    # Arrange: เตรียม section สำหรับทดสอบช่วงเวลาเกินสองชั่วโมง
    section = factories.SectionFactory()
    client.force_login(admin_user)

    # Act: ส่งข้อมูลเวลาที่ยาวเกินสองชั่วโมง
    response = client.post(
        reverse("courses:time-add", args=[section.pk]),
        data={"day": "TUE", "start_time": "08:00", "end_time": "11:05"},
    )

    # Assert: มี non_field_errors และยังไม่มี ClassTime ใหม่
    form = response.context["form"]
    assert form.non_field_errors()
    assert ClassTime.objects.filter(section=section).count() == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_time_add_blocks_room_overlap(client, admin_user):
    # Arrange: สร้าง section สองชุดใช้ห้องเดียวกันและมีเวลาทับซ้อน
    room = factories.RoomFactory()
    semester = factories.SemesterFactory()
    section_existing = factories.SectionFactory(room=room, semester=semester)
    section_target = factories.SectionFactory(room=room, semester=semester)
    ClassTime.objects.create(
        section=section_existing,
        day="WED",
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    client.force_login(admin_user)

    # Act: ส่งเวลาที่ทับกับ class เดิมในห้องเดียวกัน
    response = client.post(
        reverse("courses:time-add", args=[section_target.pk]),
        data={"day": "WED", "start_time": "09:30", "end_time": "10:30"},
    )

    # Assert: ฟอร์มแจ้งข้อความเกี่ยวกับห้องซ้ำและไม่สร้าง ClassTime
    form = response.context["form"]
    errors = " ".join(form.non_field_errors())
    assert section_existing.course.name in errors
    assert "ทับ" in errors
    assert ClassTime.objects.filter(section=section_target).count() == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_time_add_blocks_instructor_overlap(client, admin_user):
    # Arrange: สร้างอาจารย์คนเดียวกันสอนสอง section พร้อมเวลาทับซ้อน
    semester = factories.SemesterFactory()
    section_primary = factories.SectionFactory(semester=semester)
    section_conflict = factories.SectionFactory(semester=semester)
    instructor_profile = factories.StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        acdemic_title=Profile.AcademicTitle.LECTURER,
        department=section_primary.course.department,
    )
    instructor_user = instructor_profile.user
    section_primary.instructors.add(instructor_user)
    section_conflict.instructors.add(instructor_user)
    ClassTime.objects.create(
        section=section_conflict,
        day="THU",
        start_time=time(14, 0),
        end_time=time(15, 0),
    )
    client.force_login(admin_user)

    # Act: ส่งเวลาที่ทับซ้อนกับอาจารย์คนเดิม
    response = client.post(
        reverse("courses:time-add", args=[section_primary.pk]),
        data={"day": "THU", "start_time": "14:30", "end_time": "15:30"},
    )

    # Assert: ฟอร์มแจ้งข้อผิดพลาดระบุชื่อผู้สอนและไม่สร้าง ClassTime
    form = response.context["form"]
    errors = " ".join(form.non_field_errors())
    assert instructor_user.username in errors
    assert ClassTime.objects.filter(section=section_primary).count() == 0
