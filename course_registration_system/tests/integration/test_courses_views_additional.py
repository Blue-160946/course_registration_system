from datetime import datetime, time as time_obj

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from courses.models import ClassTime
from payment.models import PaymentTransaction
from payment import payment_gateway
from tests import factories
from tests.conftest import freeze_time

@pytest.mark.integration
@pytest.mark.django_db
def test_course_list_view_shows_courses(client, admin_user):
    # Arrange: มีคอร์สในระบบและล็อกอินเป็น staff
    course = factories.CourseFactory()
    client.force_login(admin_user)

    # Act: เปิดหน้า list
    response = client.get(reverse("courses:course-list"))

    # Assert: สถานะ 200 และมีคอร์สใน context
    assert response.status_code == 200
    assert course in list(response.context["courses"])

@pytest.mark.integration
@pytest.mark.django_db
def test_course_edit_get_includes_object(client, admin_user):
    # Arrange: เตรียมคอร์สให้แก้ไข
    course = factories.CourseFactory()
    client.force_login(admin_user)

    # Act: เปิดหน้าแก้ไขแบบ GET
    response = client.get(reverse("courses:course-edit", args=[course.pk]))

    # Assert: ต้องมี object ใน context
    assert response.status_code == 200
    assert response.context["object"] == course

@pytest.mark.integration
@pytest.mark.django_db
def test_course_delete_get_renders_confirm(client, admin_user):
    # Arrange: เตรียมคอร์สให้ลบ
    course = factories.CourseFactory()
    client.force_login(admin_user)

    # Act: เปิดหน้าคอนเฟิร์มลบ
    response = client.get(reverse("courses:course-delete", args=[course.pk]))

    # Assert: ต้องมี object ให้ template ใช้
    assert response.status_code == 200
    assert response.context["object"] == course

@pytest.mark.integration
@pytest.mark.django_db
def test_section_list_view_shows_sections(client, admin_user):
    # Arrange: มี Section ของคอร์ส
    section = factories.SectionFactory()
    client.force_login(admin_user)

    # Act: เปิดหน้ารายการ section
    response = client.get(reverse("courses:section-list", args=[section.course.pk]))

    # Assert: context ต้องมี section ที่สร้างไว้
    assert response.status_code == 200
    assert section in list(response.context["sections"])

@pytest.mark.integration
@pytest.mark.django_db
def test_section_add_get_provides_form(client, admin_user):
    # Arrange: เตรียมคอร์สแล้วล็อกอิน
    course = factories.CourseFactory()
    client.force_login(admin_user)

    # Act: เปิดหน้าเพิ่ม section แบบ GET
    response = client.get(reverse("courses:section-add", args=[course.pk]))

    # Assert: มีฟอร์มและระบุคอร์สใน context
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["course"] == course

@pytest.mark.integration
@pytest.mark.django_db
def test_section_edit_get_includes_section(client, admin_user):
    # Arrange: มี Section ให้แก้ไข
    section = factories.SectionFactory()
    client.force_login(admin_user)

    # Act: เปิดหน้าแก้ไข
    response = client.get(reverse("courses:section-edit", args=[section.pk]))

    # Assert: context ต้องอ้างถึง section เดิม
    assert response.status_code == 200
    assert response.context["object"] == section

@pytest.mark.integration
@pytest.mark.django_db
def test_section_delete_get_renders_confirmation(client, admin_user):
    # Arrange: เลือก Section สำหรับลบ
    section = factories.SectionFactory()
    client.force_login(admin_user)

    # Act: เปิดหน้า confirm delete
    response = client.get(reverse("courses:section-delete", args=[section.pk]))

    # Assert: สถานะ 200 และ context มี object
    assert response.status_code == 200
    assert response.context["object"] == section

@pytest.mark.integration
@pytest.mark.django_db
def test_time_list_view_lists_class_times(client, admin_user):
    # Arrange: สร้างเวลาเรียนไว้หนึ่งรายการ
    section = factories.SectionFactory()
    class_time = ClassTime.objects.create(
        section=section,
        day="MON",
        start_time=time_obj(9, 0),
        end_time=time_obj(10, 0),
    )
    client.force_login(admin_user)

    # Act: เปิดหน้า time list
    response = client.get(reverse("courses:time-list", args=[section.pk]))

    # Assert: context ต้องมี class_time ที่สร้างไว้
    assert response.status_code == 200
    assert class_time in list(response.context["class_times"])

@pytest.mark.integration
@pytest.mark.django_db
def test_time_add_get_provides_form(client, admin_user):
    # Arrange: เตรียม section และล็อกอิน
    section = factories.SectionFactory()
    client.force_login(admin_user)

    # Act: เปิดหน้าเพิ่มเวลาเรียน
    response = client.get(reverse("courses:time-add", args=[section.pk]))

    # Assert: มีฟอร์มให้กรอก
    assert response.status_code == 200
    assert "form" in response.context

@pytest.mark.integration
@pytest.mark.django_db
def test_time_edit_overlap_adds_error(client, admin_user):
    # Arrange: มีเวลาเรียนอีกช่วงที่ซ้อนเวลา
    section = factories.SectionFactory()
    ClassTime.objects.create(
        section=section,
        day="TUE",
        start_time=time_obj(10, 0),
        end_time=time_obj(11, 0),
    )
    target = ClassTime.objects.create(
        section=section,
        day="TUE",
        start_time=time_obj(8, 0),
        end_time=time_obj(9, 0),
    )
    client.force_login(admin_user)
    payload = {
        "day": "TUE",
        "start_time": "10:30",
        "end_time": "11:30",
    }

    # Act: แก้ไขเวลาให้ทับกับช่วงอื่น
    response = client.post(
        reverse("courses:time-edit", args=[target.pk]),
        data=payload,
    )

    # Assert: ต้องแสดง error ว่าซ้ำซ้อนและไม่ redirect
    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    assert any("ซ้อนทับกัน" in msg for msg in response.context["form"].non_field_errors())

@pytest.mark.integration
@pytest.mark.django_db
def test_time_edit_get_populates_form(client, admin_user):
    # Arrange: มีเวลาเรียนให้แก้ไข
    class_time = ClassTime.objects.create(
        section=factories.SectionFactory(),
        day="WED",
        start_time=time_obj(12, 0),
        end_time=time_obj(13, 0),
    )
    client.force_login(admin_user)

    # Act: เปิดหน้าแก้ไขด้วย GET
    response = client.get(reverse("courses:time-edit", args=[class_time.pk]))

    # Assert: ฟอร์มถูกสร้างพร้อม object
    assert response.status_code == 200
    assert response.context["object"] == class_time

@pytest.mark.integration
@pytest.mark.django_db
def test_time_delete_get_renders_confirmation(client, admin_user):
    # Arrange: มีเวลาเรียนให้ลบ
    class_time = ClassTime.objects.create(
        section=factories.SectionFactory(),
        day="THU",
        start_time=time_obj(14, 0),
        end_time=time_obj(15, 0),
    )
    client.force_login(admin_user)

    # Act: เปิดหน้า confirm delete
    response = client.get(reverse("courses:time-delete", args=[class_time.pk]))

    # Assert: status 200 และส่ง object ให้ template
    assert response.status_code == 200
    assert response.context["object"] == class_time

@pytest.mark.integration
@pytest.mark.django_db
def test_my_schedule_view_filters_current_semester(client, student_user):
    # Arrange: ผูกนักศึกษากับ Section ในเทอมปัจจุบัน
    semester = factories.SemesterFactory()
    section_current = factories.SectionFactory(semester=semester)
    section_other = factories.SectionFactory()
    student_user.enrolled_sections.add(section_current, section_other)
    client.force_login(student_user)
    mocked_now = timezone.make_aware(datetime(2024, 1, 20))

    # Act: เรียก view พร้อม freeze เวลาให้อยู่ในเทอม
    with freeze_time(mocked_now):
        response = client.get(reverse("courses:my-schedule"))

    # Assert: context ต้องเหลือแค่ section ของเทอมปัจจุบัน
    assert response.status_code == 200
    got = list(response.context["enrolled_sections"])
    assert set(got) == {section_current}
    assert response.context["current_semester"] == semester

@pytest.mark.integration
@pytest.mark.django_db
def test_enroll_section_prevents_duplicate_registration(client, student_user):
    # Arrange: ให้นักศึกษาลงทะเบียน section ไว้ก่อน
    section = factories.SectionFactory()
    section.students.add(student_user)
    client.force_login(student_user)

    # Act: พยายามลงทะเบียนซ้ำ
    response = client.post(
        reverse("courses:enroll-section", args=[section.pk]),
        follow=True,
    )

    # Assert: ถูก redirect พร้อม warning ข้อความเกี่ยวกับ Sec
    assert response.redirect_chain[-1][0].endswith(reverse("courses:public-section-list"))
    messages = list(get_messages(response.wsgi_request))
    assert any("กลุ่มเรียนที่" in message.message for message in messages)

@pytest.mark.integration
@pytest.mark.django_db
def test_enroll_section_handles_payment_failure(client, student_user, monkeypatch):
    # Arrange: สร้าง section ที่มีค่าใช้จ่ายและ mock payment ล้มเหลว
    section = factories.SectionFactory()
    client.force_login(student_user)
    monkeypatch.setattr(
        payment_gateway.FakePaymentGateway,
        "charge",
        staticmethod(lambda student, amount: {"success": False, "transaction_id": "FAIL-001"}),
    )

    # Act: เรียก view เพื่อชำระเงินแล้วล้มเหลว
    response = client.post(
        reverse("courses:enroll-section", args=[section.pk]),
        follow=True,
    )

    # Assert: ต้อง redirect และบันทึก PaymentTransaction สถานะ FAILED
    assert response.redirect_chain[-1][0].endswith(reverse("courses:public-section-list"))
    messages = list(get_messages(response.wsgi_request))
    assert any("ล้มเหลว" in message.message for message in messages)
    assert PaymentTransaction.objects.filter(
        student=student_user.profile,
        course=section.course,
        status="FAILED",
    ).exists()
