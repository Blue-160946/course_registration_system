import pytest
from hypothesis import assume, given, strategies as st
from django.core.exceptions import ValidationError

from users.models import Profile
from courses.models import Course


def _course_code_validator():
    """ช่วยดึง validator ของรหัสวิชา"""
    return Course._meta.get_field("code").validators[0]

@pytest.mark.unit
@given(st.text(min_size=8, max_size=8, alphabet=st.characters(min_codepoint=48, max_codepoint=57)))
def test_student_id_validator_accepts_all_digit_strings(value):
    """property: สตริงความยาว 8 ที่เป็นตัวเลขล้วนต้องผ่านเสมอ"""
    Profile.student_id_validator(value)

@pytest.mark.unit
@given(st.text())
def test_student_id_validator_rejects_non_digit_or_wrong_length(value):
    """property: ถ้าไม่ใช่ตัวเลขล้วน หรือความยาว != 8 ต้องถูกปฏิเสธ"""
    assume(not (len(value) == 8 and value.isdigit()))
    with pytest.raises(ValidationError):
        Profile.student_id_validator(value)

@pytest.mark.unit
@given(st.text(min_size=6, max_size=6, alphabet=st.characters(min_codepoint=48, max_codepoint=57)))
def test_course_code_validator_accepts_six_digits(value):
    """property: รหัสวิชาที่เป็นตัวเลข 6 หลักต้องผ่าน validator"""
    validator = _course_code_validator()
    validator(value)

@pytest.mark.unit
@given(st.text())
def test_course_code_validator_rejects_other_patterns(value):
    """property: รูปแบบอื่นนอกเหนือจากตัวเลข 6 หลักต้องถูกปฏิเสธ"""
    from hypothesis import assume

    assume(not (len(value) == 6 and value.isdigit()))
    validator = _course_code_validator()
    with pytest.raises(ValidationError):
        validator(value)
