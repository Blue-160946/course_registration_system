import pytest
from courses.forms import SectionForm, ClassTimeForm, ClassTimeFormSet
from courses.models import Section, Room, Semester, Department, Faculty
from django.contrib.auth.models import User
from users.models import Profile
from datetime import date

@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="วิทยาศาสตร์")

@pytest.fixture
def department(db, faculty):
    return Department.objects.create(name="คอมพิวเตอร์", faculty=faculty)

@pytest.fixture
def room(db):
    return Room.objects.create(building="A", room_number="101")

@pytest.fixture
def semester(db):
    return Semester.objects.create(
        year=2567, semester=1,
        start_date=date(2025, 6, 1), end_date=date(2025, 10, 1)
    )

@pytest.mark.django_db
def test_section_form_valid(department, room, semester):
    user = User.objects.create(username='i')
    Profile.objects.create(user=user, user_type='INSTRUCTOR')
    form = SectionForm(data={
        'semester': semester.pk,
        'section_number': '1',
        'room': room.pk,
        'capacity': 10,
        'instructors': [user.pk],
    })
    assert form.is_valid()

@pytest.mark.django_db
def test_section_form_no_instructor(department, room, semester):
    form = SectionForm(data={
        'semester': semester.pk,
        'section_number': '1',
        'room': room.pk,
        'capacity': 10,
        'instructors': [],
    })
    assert not form.is_valid()
    assert 'instructors' in form.errors

@pytest.mark.django_db
def test_classtime_form_invalid_time():
    form = ClassTimeForm(data={
        'day': 'MON',
        'start_time': '13:00',
        'end_time': '12:00',
    })
    assert not form.is_valid()
    assert 'end_time' in form.errors

@pytest.mark.django_db
def test_classtime_form_missing_fields():
    form = ClassTimeForm(data={
        'day': '',
        'start_time': '',
        'end_time': '',
    })
    assert not form.is_valid()  # ต้องเป็น False เพราะทุก field required

@pytest.mark.django_db
def test_classtime_formset_must_have_at_least_one():
    formset = ClassTimeFormSet(data={
        'class_times-TOTAL_FORMS': 0,
        'class_times-INITIAL_FORMS': 0,
        'class_times-MIN_NUM_FORMS': 0,
        'class_times-MAX_NUM_FORMS': 1000,
    })
    assert not formset.is_valid()
    errors = formset.non_form_errors()
    assert any('กรุณากรอกข้อมูลคาบเรียนอย่างน้อย 1 คาบเรียน' in e for e in errors)