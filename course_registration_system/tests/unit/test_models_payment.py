import pytest

from payment.models import PaymentTransaction
from tests.factories import CourseFactory, StudentFactory

@pytest.mark.unit
@pytest.mark.django_db
def test_payment_transaction_str_contains_status():
    """ตรวจว่า __str__ แสดงสถานะธุรกรรม"""
    # Arrange
    profile = StudentFactory()
    course = CourseFactory()
    transaction = PaymentTransaction.objects.create(
        student=profile,
        course=course,
        amount=1500,
        status="SUCCESS",
        transaction_id="TX123",
    )

    # Act
    result = str(transaction)

    # Assert
    assert str(profile) in result
    assert "SUCCESS" in result
