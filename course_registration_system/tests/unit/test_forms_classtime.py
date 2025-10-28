import pytest

from courses.forms import ClassTimeForm
from courses.models import ClassTime
from tests.factories import SectionFactory

@pytest.mark.unit
@pytest.mark.django_db
def test_classtime_form_accepts_valid_data():
    """ตรวจว่าฟอร์มเพิ่มเวลาสอนปกติผ่านได้"""
    # Arrange
    section = SectionFactory()
    data = {
        "day": "MON",
        "start_time": "09:00",
        "end_time": "10:30",
    }

    # Act
    form = ClassTimeForm(data=data, section=section)

    # Assert
    assert form.is_valid()

@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_value,end_value,expected_key",
    [
        pytest.param("10:00", "09:00", "end_time", id="end_before_start"),
        pytest.param("09:00", "12:30", None, id="duration_too_long"),
    ],
)
def test_classtime_form_rejects_invalid_ranges(start_value, end_value, expected_key):
    """ตรวจว่าฟอร์มจับเวลาผิดปกติได้"""
    # Arrange
    section = SectionFactory()
    data = {
        "day": "MON",
        "start_time": start_value,
        "end_time": end_value,
    }

    # Act
    form = ClassTimeForm(data=data, section=section)

    # Assert
    assert form.is_valid() is False
    if expected_key:
        assert expected_key in form.errors
    else:
        assert form.non_field_errors()  # มีข้อความรวม

@pytest.mark.unit
@pytest.mark.django_db
def test_classtime_form_detects_overlap_with_existing():
    """ตรวจว่าฟอร์มไม่อนุญาตเวลาซ้อนกับที่มีอยู่"""
    # Arrange
    section = SectionFactory()
    ClassTime.objects.create(
        section=section,
        day="TUE",
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    data = {
        "day": "TUE",
        "start_time": "09:30",
        "end_time": "10:30",
    }

    # Act
    form = ClassTimeForm(data=data, section=section)

    # Assert
    assert form.is_valid() is False
    assert form.non_field_errors()
from datetime import time
