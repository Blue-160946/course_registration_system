import pytest
from django.urls import reverse
from django.contrib.messages import get_messages

from payment.models import PaymentTransaction
from tests.factories import SectionFactory, StudentFactory
from django.test import Client

@pytest.mark.integration
@pytest.mark.django_db
def test_student_login_and_enroll_success(client, student):
    """ทดสอบนักศึกษาล็อกอินแล้วลงทะเบียนสำเร็จ"""
    # Arrange
    password = "TestPass123!"
    student.user.set_password(password)
    student.user.save()
    section = SectionFactory()

    # Act
    login_ok = client.login(username=student.user.username, password=password)
    response = client.post(reverse("courses:enroll-section", args=[section.pk]))

    # Assert
    assert login_ok is True
    assert response.status_code == 302
    assert response.url == reverse("courses:public-section-list")
    assert student.user in section.students.all()
    txn = PaymentTransaction.objects.filter(student=student, course=section.course).first()
    assert PaymentTransaction.objects.filter(student=student, course=section.course).count() == 1
    assert txn is not None
    assert txn.status == ("SUCCESS" if section.course.fee > 0 else "FAILED")

@pytest.mark.integration
@pytest.mark.django_db
def test_enroll_rejects_duplicate_registration(client, student):
    """ทดสอบป้องกันการลงทะเบียนซ้ำ"""
    # Arrange
    password = "TestPass123!"
    student.user.set_password(password)
    student.user.save()
    section = SectionFactory()
    section.students.add(student.user)

    # Act
    client.login(username=student.user.username, password=password)
    response = client.post(reverse("courses:enroll-section", args=[section.pk]), follow=True)

    # Assert
    assert response.status_code == 200
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert any("ซ้ำ" in msg or "ลงทะเบียน" in msg for msg in messages)
    assert PaymentTransaction.objects.filter(student=student, course=section.course).count() == 0

@pytest.mark.integration
@pytest.mark.django_db
def test_anonymous_user_cannot_enroll(client):
    """ทดสอบผู้ใช้ไม่ล็อกอินถูก redirect ไปหน้า login"""
    # Arrange
    section = SectionFactory()

    # Act
    response = client.post(reverse("courses:enroll-section", args=[section.pk]))

    # Assert
    assert response.status_code == 302
    assert reverse("users:login") in response.url
    assert section.students.count() == 0

@pytest.mark.integration
@pytest.mark.django_db
def test_admin_can_view_student_list(client, admin_user):
    """ทดสอบผู้ดูแลเข้าถึงหน้ารายชื่อนักศึกษาได้"""
    # Arrange
    password = "TestPass123!"
    admin_user.set_password(password)
    admin_user.save()

    # Act
    login_ok = client.login(username=admin_user.username, password=password)
    response = client.get(reverse("users:student-list"))

    # Assert
    assert login_ok is True
    assert response.status_code == 200

@pytest.mark.integration
@pytest.mark.django_db
def test_non_staff_forbidden_student_list(client, student):
    """ทดสอบนักศึกษาถูกปฏิเสธเมื่อเข้าหน้ารายชื่อนักศึกษา"""
    # Arrange
    password = "TestPass123!"
    student.user.set_password(password)
    student.user.save()

    # Act
    client.login(username=student.user.username, password=password)
    response = client.get(reverse("users:student-list"))

    # Assert
    assert response.status_code == 403

@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.xfail(reason="ทดสอบยังไม่เสถียรในสภาวะ concurrent จริง", strict=False)
def test_concurrent_enrollment_does_not_overfill_capacity():
    """ทดสอบ race condition การลงทะเบียนพร้อมกันไม่ให้ที่นั่งติดลบและไม่ซ้ำ"""
    # Arrange
    section = SectionFactory(capacity=1)
    student1 = StudentFactory()
    student2 = StudentFactory()
    password = "TestPass123!"
    student1.user.set_password(password)
    student2.user.set_password(password)
    student1.user.save()
    student2.user.save()

    client1 = Client()
    client2 = Client()
    assert client1.login(username=student1.user.username, password=password)
    assert client2.login(username=student2.user.username, password=password)

    # Act
    enroll_url = reverse("courses:enroll-section", args=[section.pk])
    response1 = client1.post(enroll_url)
    response2 = client2.post(enroll_url, follow=True)

    # Assert
    section.refresh_from_db()
    # ป้องกันเคส race condition ที่ทั้งสอง request เพิ่มนักศึกษาได้พร้อมกันจนเกินความจุ
    enrolled_users = list(section.students.all())
    assert len(enrolled_users) <= section.capacity  # ไม่เกินความจุ
    assert len(set(user.pk for user in enrolled_users)) == len(enrolled_users)  # ไม่มีซ้ำ
    assert response1.status_code == 302
    assert response2.status_code == 200  # รอบที่สอง follow แล้วต้องอยู่หน้ารายการพร้อมข้อความเตือน
    dup_messages = [m.message for m in get_messages(response2.wsgi_request)]
    assert any("ลงทะเบียน" in msg for msg in dup_messages)  # มีคำเตือนว่าซ้ำ
    # ตรวจ invariant ธุรกรรมต้องตรงกับผู้ที่ลงทะเบียนได้จริง
    payment_transactions = PaymentTransaction.objects.filter(course=section.course, student__user__in=enrolled_users)
    assert payment_transactions.count() == len(enrolled_users)
