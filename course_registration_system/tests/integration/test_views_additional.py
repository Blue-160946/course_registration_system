from datetime import date, datetime
from types import SimpleNamespace

import pytest
from django.test import Client
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone

from courses.models import ClassTime, Course, Section
from tests.conftest import freeze_time
from tests.factories import (
    CourseFactory,
    DepartmentFactory,
    RoomFactory,
    SectionFactory,
    SemesterFactory,
    StudentFactory,
)
from users.models import Profile

@pytest.mark.integration
@pytest.mark.django_db
def test_core_index_context_variants(client):
    """ตรวจ view core:index ในกรณีมี/ไม่มีภาคเรียนปัจจุบัน"""
    with freeze_time(timezone.make_aware(datetime(2024, 1, 10))):
        response_no_semester = client.get(reverse("core:index"))
        assert response_no_semester.status_code == 200
        assert response_no_semester.context["current_semester"] is None
        assert list(response_no_semester.context["sections"]) == []

        semester = SemesterFactory(start_date=date(2024, 1, 1), end_date=date(2024, 2, 1))
        section = SectionFactory(semester=semester)
        response_with_semester = client.get(reverse("core:index"))
        assert response_with_semester.context["current_semester"] == semester
        assert section in response_with_semester.context["sections"]

@pytest.mark.integration
@pytest.mark.django_db
def test_course_crud_flow(client, admin_user):
    """ตรวจการเพิ่ม/แก้ไข/ลบวิชาใน view สำหรับ staff"""
    client.force_login(admin_user)
    dept = DepartmentFactory()

    assert client.get(reverse("courses:course-add")).status_code == 200

    create_response = client.post(
        reverse("courses:course-add"),
        {
            "code": "123456",
            "name": "Software Test",
            "credits": 3,
            "department": dept.pk,
            "fee": 0,
            "description": "desc",
            "is_active": "on",
        },
    )
    assert create_response.status_code == 302
    course = Course.objects.get(code="123456")

    edit_response = client.post(
        reverse("courses:course-edit", args=[course.pk]),
        {
            "code": "123456",
            "name": "Software QA",
            "credits": 4,
            "department": dept.pk,
            "fee": 500,
            "description": "updated",
            "is_active": "on",
        },
    )
    assert edit_response.status_code == 302
    course.refresh_from_db()
    assert course.credits == 4

    delete_response = client.post(reverse("courses:course-delete", args=[course.pk]))
    assert delete_response.status_code == 302
    assert not Course.objects.filter(pk=course.pk).exists()

@pytest.mark.integration
@pytest.mark.django_db
def test_course_add_invalid_shows_form(client, admin_user):
    """ตรวจว่าการเพิ่ม course ไม่สมบูรณ์จะแสดงฟอร์มพร้อม error"""
    client.force_login(admin_user)
    response = client.post(reverse("courses:course-add"), {"code": ""})
    assert response.status_code == 200
    assert "form" in response.context


def _make_instructor(department):
    profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        department=department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    profile.first_name_th = ""
    profile.last_name_th = ""
    profile.address = "???????????????????????????"
    profile.save()
    return profile.user

@pytest.mark.integration
@pytest.mark.django_db
def test_section_crud_flow(client, admin_user):
    """ตรวจการเพิ่ม/แก้ไข/ลบ Section ผ่าน view staff"""
    client.force_login(admin_user)
    course = CourseFactory()
    semester = SemesterFactory()
    room = RoomFactory()
    instructor = _make_instructor(course.department)

    add_response = client.post(
        reverse("courses:section-add", args=[course.pk]),
        {
            "semester": semester.pk,
            "section_number": "11",
            "room": room.pk,
            "capacity": 40,
            "instructors": [instructor.pk],
        },
    )
    assert add_response.status_code == 302
    section = Section.objects.get(course=course, section_number="11")

    edit_response = client.post(
        reverse("courses:section-edit", args=[section.pk]),
        {
            "semester": semester.pk,
            "section_number": "11",
            "room": room.pk,
            "capacity": 35,
            "instructors": [instructor.pk],
        },
    )
    assert edit_response.status_code == 302
    section.refresh_from_db()
    assert section.capacity == 35

    delete_response = client.post(reverse("courses:section-delete", args=[section.pk]))
    assert delete_response.status_code == 302
    assert not Section.objects.filter(pk=section.pk).exists()

@pytest.mark.integration
@pytest.mark.django_db
def test_time_management_flows(client, admin_user):
    """ตรวจการเพิ่ม/แก้ไข/ลบ ClassTime ของ staff"""
    client.force_login(admin_user)
    section = SectionFactory()

    add_response = client.post(
        reverse("courses:time-add", args=[section.pk]),
        {"day": "MON", "start_time": "09:00", "end_time": "10:00"},
    )
    assert add_response.status_code == 302
    classtime = section.class_times.get(day="MON")

    edit_response = client.post(
        reverse("courses:time-edit", args=[classtime.pk]),
        {"day": "MON", "start_time": "09:30", "end_time": "10:30"},
    )
    assert edit_response.status_code == 302

    delete_response = client.post(reverse("courses:time-delete", args=[classtime.pk]))
    assert delete_response.status_code == 302
    assert not section.class_times.filter(pk=classtime.pk).exists()

@pytest.mark.integration
@pytest.mark.django_db
def test_time_edit_conflict_shows_form_error(client, admin_user):
    """ตรวจว่าการแก้ไขเวลาซ้อนกันแสดง error ในฟอร์ม"""
    client.force_login(admin_user)
    section = SectionFactory()
    ClassTime.objects.create(
        section=section, day="TUE", start_time="09:00", end_time="10:00"
    )
    target = ClassTime.objects.create(
        section=section, day="TUE", start_time="10:00", end_time="11:00"
    )

    response = client.post(
        reverse("courses:time-edit", args=[target.pk]),
        {"day": "TUE", "start_time": "09:30", "end_time": "10:30"},
    )

    assert response.status_code == 200
    assert response.context["form"].non_field_errors()

@pytest.mark.integration
@pytest.mark.django_db
def test_public_section_list_filters(client, student_user):
    """ตรวจการกรองรายชื่อ Section ที่แสดงต่อผู้ใช้ทั่วไป"""
    student_user.set_password("StudentPass123!")
    student_user.save()
    client.force_login(student_user)

    with freeze_time(timezone.make_aware(datetime(2024, 1, 10))):
        semester = SemesterFactory(start_date=date(2024, 1, 1), end_date=date(2024, 2, 1))
        section = SectionFactory(semester=semester)

        response_all = client.get(reverse("courses:public-section-list"))
        assert section in response_all.context["sections"]

        response_search = client.get(
            reverse("courses:public-section-list"), {"q": section.course.code}
        )
        assert section in response_search.context["sections"]

    with freeze_time(timezone.make_aware(datetime(2025, 5, 10))):
        response_no_semester = client.get(reverse("courses:public-section-list"))
        assert list(response_no_semester.context["sections"]) == []

@pytest.mark.integration
@pytest.mark.django_db
def test_course_list_permission_denied_for_non_staff(client, student_user):
    """ตรวจว่า decorator staff_required คืนค่า 403 เมื่อผู้ใช้ไม่ใช่ staff"""
    student_user.set_password("StudentPass123!")
    student_user.save()
    client.force_login(student_user)

    response = client.get(reverse("courses:course-list"))
    assert response.status_code == 403

@pytest.mark.integration
@pytest.mark.django_db
def test_my_schedule_and_pdf_success(client):
    """ตรวจการแสดงตารางเรียนและสร้างไฟล์ PDF ได้สำเร็จ"""
    profile = StudentFactory()
    user = profile.user
    user.set_password("TestPass123!")
    user.save()
    client.force_login(user)

    semester = SemesterFactory(start_date=date(2024, 1, 1), end_date=date(2024, 1, 31))
    section = SectionFactory(semester=semester)
    section.students.add(user)

    with freeze_time(timezone.make_aware(datetime(2024, 1, 10))):
        schedule_response = client.get(reverse("courses:my-schedule"))
        assert section in schedule_response.context["enrolled_sections"]

        from xhtml2pdf import pisa

        def fake_create_pdf(html, dest):
            dest.write(b"PDF")
            return SimpleNamespace(err=0)

        monkeypatcher = lambda *args, **kwargs: SimpleNamespace(err=0)
        original = pisa.CreatePDF
        pisa.CreatePDF = monkeypatcher
        try:
            pdf_response = client.get(reverse("courses:my-schedule-pdf"))
        finally:
            pisa.CreatePDF = original

    assert pdf_response.status_code == 200
    assert pdf_response["Content-Type"] == "application/pdf"

@pytest.mark.integration
@pytest.mark.django_db
def test_my_schedule_pdf_failure_returns_html(client, monkeypatch):
    """ตรวจว่าเมื่อสร้าง PDF ล้มเหลว ระบบส่งหน้า HTML แทน"""
    profile = StudentFactory()
    user = profile.user
    user.set_password("TestPass123!")
    user.save()
    client.force_login(user)

    monkeypatch.setattr(
        "courses.views.pisa.CreatePDF",
        lambda html, dest: SimpleNamespace(err=1),
    )

    response = client.get(reverse("courses:my-schedule-pdf"))
    assert response.status_code == 200
    assert "PDF" in response.content.decode()

@pytest.mark.integration
@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
@pytest.mark.django_db
def test_staff_login_view_branches(client, admin_user):
    """ตรวจพฤติกรรม staff_login_view เมื่อ login เป็น staff / student / ข้อมูลผิด"""
    login_url = reverse("users:login")
    admin_user.set_password("AdminPass123!")
    admin_user.save()

    client.force_login(admin_user)
    assert client.get(login_url).status_code == 302
    client.logout()

    response_staff = client.post(
        login_url,
        {"username": admin_user.username, "password": "AdminPass123!"},
        follow=False,
    )
    assert response_staff.status_code == 302
    assert response_staff.headers["Location"].endswith(reverse("courses:course-list"))

    student_profile = StudentFactory()
    student_profile.user.set_password("StudentPass123!")
    student_profile.user.save()
    student_client = Client()
    response_student = student_client.post(
        login_url,
        {"username": student_profile.user.username, "password": "StudentPass123!"},
        follow=False,
    )
    assert response_student.status_code == 302
    assert response_student.headers["Location"].endswith(
        reverse("courses:public-section-list")
    )

    bad_response = client.post(login_url, {"username": "wrong", "password": "wrong"}, follow=True)
    assert bad_response.status_code == 200

@pytest.mark.integration
@pytest.mark.django_db
def test_student_list_and_detail_permissions(client, admin_user):
    """ตรวจสิทธิ์เข้าถึงหน้า student list/detail ของ staff เท่านั้น"""
    admin_user.set_password("AdminPass123!")
    admin_user.save()
    client.force_login(admin_user)

    student_profile = StudentFactory()
    assert client.get(reverse("users:student-list")).status_code == 200
    assert (
        client.get(reverse("users:student-detail", args=[student_profile.user.pk])).status_code
        == 200
    )

    client.logout()
    student_profile.user.set_password("StudentPass123!")
    student_profile.user.save()
    client.force_login(student_profile.user)
    assert client.get(reverse("users:student-list")).status_code == 403
