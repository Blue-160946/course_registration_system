import pytest
from django.core.exceptions import ValidationError

from users.models import Profile

@pytest.mark.unit
def test_student_id_validator_accepts_digits():
    """ตรวจว่า validator รับค่าตัวเลข 8 หลัก"""
    # Arrange
    validator = Profile.student_id_validator

    # Act / Assert
    validator("12345678")

@pytest.mark.unit
@pytest.mark.parametrize(
    "student_id",
    ["ABCDEFGH", "1234", "12-345678"],
)
def test_student_id_validator_rejects_invalid_patterns(student_id):
    """ตรวจว่า validator ปฏิเสธรูปแบบอื่น"""
    # Arrange
    validator = Profile.student_id_validator

    # Act / Assert
    with pytest.raises(ValidationError):
        validator(student_id)

@pytest.mark.unit
@pytest.mark.parametrize(
    "value",
    ["สมชาย", "ทดสอบ นามสกุล"],
)
def test_thai_validator_accepts_thai_text(value):
    """ตรวจว่าข้อความไทยผ่านการตรวจสอบ"""
    # Arrange
    validator = Profile.thai_validator

    # Act / Assert
    validator(value)

@pytest.mark.unit
@pytest.mark.parametrize(
    "value",
    ["John", "123ทดสอบ"],
)
def test_thai_validator_rejects_non_thai(value):
    """ตรวจว่ามีตัวอักษรอื่นแล้วไม่ผ่าน"""
    # Arrange
    validator = Profile.thai_validator

    # Act / Assert
    with pytest.raises(ValidationError):
        validator(value)
