import pytest
from django.contrib import messages
from django.contrib.messages import get_messages
from django.urls import reverse

from payment.models import PaymentTransaction
from payment import payment_gateway
from tests import factories


@pytest.mark.integration
@pytest.mark.django_db
def test_enroll_section_processes_payment_success(client, student_user):
    # Arrange: เตรียม section ที่มีค่าธรรมเนียมเพื่อทดสอบการตัดเงินสำเร็จ
    section = factories.SectionFactory()
    client.force_login(student_user)

    # Act: ส่งคำขอ enroll section ที่ต้องชำระเงิน
    response = client.post(
        reverse("courses:enroll-section", args=[section.pk]),
        follow=True,
    )

    # Assert: บันทึก PaymentTransaction สถานะ SUCCESS และมีข้อความแจ้งเตือนสำเร็จ
    assert response.redirect_chain[-1][0].endswith(reverse("courses:public-section-list"))
    txn = PaymentTransaction.objects.get(student=student_user.profile, course=section.course)
    assert txn.status == "SUCCESS"
    assert txn.transaction_id == "TXN-DETERMINISTIC"
    flash_messages = list(get_messages(response.wsgi_request))
    assert any(
        section.course.name in msg.message and msg.level == messages.SUCCESS
        for msg in flash_messages
    )


@pytest.mark.integration
@pytest.mark.django_db
def test_enroll_section_handles_payment_timeout_as_failure(client, student_user, monkeypatch):
    # Arrange: จำลอง FakePaymentGateway ให้ตอบกลับ timeout
    section = factories.SectionFactory()
    client.force_login(student_user)

    def fake_timeout(student, amount):
        return {"success": False, "transaction_id": "TIMEOUT", "error": "timeout"}

    monkeypatch.setattr(
        payment_gateway.FakePaymentGateway,
        "charge",
        staticmethod(fake_timeout),
    )

    # Act: ส่งคำขอ enroll แล้วถูกปฏิเสธเพราะ timeout
    response = client.post(
        reverse("courses:enroll-section", args=[section.pk]),
        follow=True,
    )

    # Assert: เกิดการ redirect พร้อมสร้าง PaymentTransaction สถานะ FAILED
    assert response.redirect_chain[-1][0].endswith(reverse("courses:public-section-list"))
    txn = PaymentTransaction.objects.get(student=student_user.profile, course=section.course)
    assert txn.status == "FAILED"
    assert txn.transaction_id is None
    flash_messages = list(get_messages(response.wsgi_request))
    assert any(
        section.course.name in msg.message and msg.level == messages.ERROR
        for msg in flash_messages
    )
