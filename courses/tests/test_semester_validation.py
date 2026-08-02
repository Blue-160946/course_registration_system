from datetime import date

import pytest
from django.core.exceptions import ValidationError

from courses.models import Semester


@pytest.mark.django_db
def test_summer_semester_accepts_thirty_days():
    semester = Semester(
        year=2569,
        semester=3,
        start_date=date(2026, 4, 1),
        end_date=date(2026, 5, 1),
    )

    semester.full_clean()


@pytest.mark.django_db
def test_regular_semester_requires_ninety_days():
    semester = Semester(
        year=2569,
        semester=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 31),
    )

    with pytest.raises(ValidationError):
        semester.full_clean()


@pytest.mark.django_db
def test_semester_date_ranges_cannot_overlap():
    Semester.objects.create(
        year=2569,
        semester=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 4, 1),
    )
    overlapping = Semester(
        year=2569,
        semester=2,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 6, 1),
    )

    with pytest.raises(ValidationError, match='ซ้อนทับ'):
        overlapping.full_clean()
