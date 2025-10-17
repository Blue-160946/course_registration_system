import pytest
from datetime import date
from django.contrib.auth.models import User, Group
from courses.models import Course, Section, Semester, Room, Department, Faculty, Profile

@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="วิทยาศาสตร์")

@pytest.fixture
def department(db, faculty):
    return Department.objects.create(name="คอมพิวเตอร์", faculty=faculty)

@pytest.fixture
def course(db, department):
    return Course.objects.create(
        code="CS101", name="Programming",
        department=department, credits=3, description="Intro", is_active=True
    )

@pytest.fixture
def semester(db):
    return Semester.objects.create(
        year=2567, semester=1,
        start_date=date(2025, 6, 1), end_date=date(2025, 10, 1)
    )

@pytest.fixture
def room(db):
    return Room.objects.create(building="A", room_number="101")

@pytest.fixture
def staff_group(db):
    return Group.objects.get_or_create(name="staff")[0]

@pytest.fixture
def instructor_group(db):
    return Group.objects.get_or_create(name="instructor")[0]

@pytest.fixture
def student_group(db):
    return Group.objects.get_or_create(name="student")[0]

@pytest.fixture
def staff_user(db, staff_group):
    user = User.objects.create_user(username="admin", password="123456789", is_staff=True)
    user.groups.add(staff_group)
    Profile.objects.create(user=user, user_type="ADMIN")
    return user

@pytest.fixture
def instructor_user(db, instructor_group):
    user = User.objects.create_user(username="instructor", password="pass123")
    user.groups.add(instructor_group)
    Profile.objects.create(user=user, user_type="INSTRUCTOR",
                           first_name_th="สมชาย", last_name_th="ใจดี")
    return user

@pytest.fixture
def student_user(db, student_group):
    user = User.objects.create_user(username="student", password="pass123")
    user.groups.add(student_group)
    Profile.objects.create(user=user, user_type="STUDENT")
    return user

@pytest.fixture
def section(db, course, semester, room, instructor_user):
    s = Section.objects.create(
        course=course, section_number="1", semester=semester, room=room, capacity=30
    )
    s.instructors.add(instructor_user)
    return s
