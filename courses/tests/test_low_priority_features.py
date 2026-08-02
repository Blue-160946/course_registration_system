from datetime import date

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from courses.models import Branch, Department, Faculty, Room, Semester
from payment.models import PaymentTransaction
from users.models import Profile
from courses.tests.test_enrollment.factories import CourseFactory, ProfileFactory


@pytest.fixture
def staff_user(db):
    user = User.objects.create_user(
        username='master-data-staff',
        password='pass1234',
        is_staff=True,
    )
    Profile.objects.create(
        user=user,
        user_type=Profile.UserType.STAFF,
        job_title=Profile.JobTitle.REGISTRATION_OFFICER,
    )
    return user


@pytest.mark.django_db
def test_staff_can_open_every_master_data_list(client, staff_user):
    faculty = Faculty.objects.create(name='วิทยาศาสตร์')
    department = Department.objects.create(name='คอมพิวเตอร์', faculty=faculty)
    Branch.objects.create(name='วิทยาการคอมพิวเตอร์', department=department)
    Room.objects.create(building='อาคาร A', room_number='101')
    Semester.objects.create(
        year=2569,
        semester=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 4, 1),
    )
    client.force_login(staff_user)

    assert client.get(reverse('courses:master-data-index')).status_code == 200
    for kind in ('faculties', 'departments', 'branches', 'rooms', 'semesters'):
        response = client.get(reverse('courses:master-data-list', kwargs={'kind': kind}))
        assert response.status_code == 200


@pytest.mark.django_db
def test_staff_can_create_edit_and_delete_faculty(client, staff_user):
    client.force_login(staff_user)

    create_response = client.post(
        reverse('courses:master-data-add', kwargs={'kind': 'faculties'}),
        {'name': 'วิทยาศาสตร์'},
    )
    assert create_response.status_code == 302
    faculty = Faculty.objects.get(name='วิทยาศาสตร์')

    edit_response = client.post(
        reverse(
            'courses:master-data-edit',
            kwargs={'kind': 'faculties', 'pk': faculty.pk},
        ),
        {'name': 'วิศวกรรมศาสตร์'},
    )
    assert edit_response.status_code == 302
    faculty.refresh_from_db()
    assert faculty.name == 'วิศวกรรมศาสตร์'

    delete_response = client.post(
        reverse(
            'courses:master-data-delete',
            kwargs={'kind': 'faculties', 'pk': faculty.pk},
        )
    )
    assert delete_response.status_code == 302
    assert not Faculty.objects.filter(pk=faculty.pk).exists()


@pytest.mark.django_db
def test_student_cannot_manage_master_data(client):
    student_profile = ProfileFactory(user_type=Profile.UserType.STUDENT)
    client.force_login(student_profile.user)

    assert client.get(reverse('courses:master-data-index')).status_code == 403
    assert client.get(
        reverse('courses:master-data-list', kwargs={'kind': 'faculties'})
    ).status_code == 403


@pytest.mark.django_db
def test_student_and_staff_can_view_payment_history(client):
    student_profile = ProfileFactory(user_type=Profile.UserType.STUDENT)
    course = CourseFactory(fee=500)
    payment = PaymentTransaction.objects.create(
        student=student_profile,
        course=course,
        amount=500,
        status='SUCCESS',
        transaction_id='TX-HISTORY-001',
    )

    client.force_login(student_profile.user)
    student_response = client.get(reverse('users:payment-history'))
    assert student_response.status_code == 200
    assert payment.transaction_id.encode() in student_response.content

    staff = User.objects.create_user(
        username='history-staff',
        password='pass1234',
        is_staff=True,
    )
    Profile.objects.create(
        user=staff,
        user_type=Profile.UserType.STAFF,
        job_title=Profile.JobTitle.REGISTRATION_OFFICER,
    )
    client.force_login(staff)
    detail_response = client.get(
        reverse('users:student-detail', kwargs={'pk': student_profile.user.pk})
    )
    assert detail_response.status_code == 200
    assert payment.transaction_id.encode() in detail_response.content
