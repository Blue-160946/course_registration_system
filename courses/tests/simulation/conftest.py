import pytest
from datetime import date, time, timedelta
from django.contrib.auth.models import User
from courses.models import (
    Faculty, Department, Branch, Course,
    Semester, Room, Section, ClassTime
)
from users.models import Profile


# ---------------------------
# Faculty / Department / Branch
# ---------------------------
@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="คณะวิทยาศาสตร์")

@pytest.fixture
def department(db, faculty):
    return Department.objects.create(name="ภาควิชาคอมพิวเตอร์", faculty=faculty)

@pytest.fixture
def branch(db, department):
    return Branch.objects.create(name="สาขาวิชาวิทยาการคอมพิวเตอร์", department=department)


# ---------------------------
# Semester
# ---------------------------
@pytest.fixture
def semester(db):
    return Semester.objects.create(
        year=2568,
        semester=1,
        start_date=date(2025, 6, 1),
        end_date=date(2025, 12, 31),
    )


# ---------------------------
# Room
# ---------------------------
@pytest.fixture
def room(db):
    return Room.objects.create(building="SC1", room_number="101")


# ---------------------------
# Users & Profiles
# ---------------------------
@pytest.fixture
def instructor_user(db, department):
    user = User.objects.create_user(username="instructor1", password="testpass")
    Profile.objects.create(
        user=user,
        user_type=Profile.UserType.INSTRUCTOR,
        first_name_th="สมชาย",
        last_name_th="ใจดี",
        acdemic_title=Profile.AcademicTitle.LECTURER,
        department=department,
    )
    return user

@pytest.fixture
def student_user(db, branch):
    user = User.objects.create_user(username="student1", password="testpass")
    Profile.objects.create(
        user=user,
        user_type=Profile.UserType.STUDENT,
        first_name_th="สมศรี",
        last_name_th="เรียนดี",
        student_id="65000001",
        branch=branch,
        student_status=Profile.StudentStatus.STUDYING,
    )
    return user


# ---------------------------
# Course
# ---------------------------
@pytest.fixture
def course(db, department):
    return Course.objects.create(
        department=department,
        code="123456",
        name="วิทยาการคอมพิวเตอร์เบื้องต้น",
        credits=3,
        description="รายวิชาแนะนำเบื้องต้น",
        fee=1500.00,
    )


# ---------------------------
# Section
# ---------------------------
@pytest.fixture
def section(db, course, semester, room, instructor_user):
    section = Section.objects.create(
        course=course,
        semester=semester,
        section_number="1",
        capacity=40,
        room=room,
    )
    section.instructors.add(instructor_user)
    return section


# ---------------------------
# ClassTime
# ---------------------------
@pytest.fixture
def classtime(db, section):
    return ClassTime.objects.create(
        section=section,
        day="MON",
        start_time=time(9, 0),
        end_time=time(11, 0),
    )
