from datetime import date, datetime

import pytest
from django.core.exceptions import ValidationError

from tests.factories import SemesterFactory
from courses.models import Semester

@pytest.mark.unit
@pytest.mark.django_db
def test_semester_clean_accepts_valid_range():
    """ตรวจว่า full_clean ผ่านเมื่อข้อมูลภาคเรียนถูกต้อง"""
    # Arrange
    semester = SemesterFactory.build(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 8, 1),
        year=2567,
        semester=1,
    )

    # Act / Assert
    semester.full_clean()

@pytest.mark.unit
@pytest.mark.django_db
def test_semester_str_contains_year():
    """ตรวจว่า __str__ แสดงปีการศึกษาที่คาดไว้"""
    # Arrange
    semester = SemesterFactory.build(year=2567, semester=1)

    # Act
    result = str(semester)

    # Assert
    assert "2567" in result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_date,end_date,year,expected_field",
    [
        pytest.param(
            date(2024, 3, 1),
            date(2024, 2, 1),
            2567,
            "end_date",
            id="end_before_start",
        ),
        pytest.param(
            date(2024, 1, 1),
            date(2024, 3, 1),
            2567,
            None,
            id="duration_too_short",
        ),
        pytest.param(
            date(2024, 1, 1),
            date(2024, 9, 1),
            datetime.now().year + 543 + 2,
            "year",
            id="year_too_far",
        ),
    ],
)
def test_semester_clean_rejects_invalid_ranges(start_date, end_date, year, expected_field):
    """ตรวจว่า full_clean ยก ValidationError ตามเงื่อนไขผิด"""
    # Arrange
    semester = Semester(
        year=year,
        semester=1,
        start_date=start_date,
        end_date=end_date,
    )

    # Act / Assert
    with pytest.raises(ValidationError) as exc_info:
        semester.full_clean()

    # Assert
    if expected_field:
        assert expected_field in exc_info.value.error_dict  # ตรวจว่าฟิลด์ถูกชี้เป้า
    else:
        assert exc_info.value.messages  # มีข้อความผิดปกติทั่วไปกลับมา
