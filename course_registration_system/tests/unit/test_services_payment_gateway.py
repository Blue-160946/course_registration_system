import pytest

from payment.payment_gateway import FakePaymentGateway

@pytest.mark.unit
@pytest.mark.parametrize(
    "amount,expected_success,expected_txn",
    [
        pytest.param(0, False, "FREE-COURSE", id="free_course_fail"),
        pytest.param(1500, True, "TXN-DETERMINISTIC", id="paid_course_success"),
    ],
)
def test_fake_payment_gateway_charge(amount, expected_success, expected_txn, student):
    """ตรวจการทำงานของเกตเวย์จำลองให้ได้ผลลัพธ์คงที่"""
    # Arrange
    student_user = student.user

    # Act
    result = FakePaymentGateway.charge(student_user, amount)

    # Assert
    assert result["success"] is expected_success
    assert result["transaction_id"] == expected_txn
