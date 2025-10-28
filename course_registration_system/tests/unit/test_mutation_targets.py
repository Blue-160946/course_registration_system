import pytest
from django.urls import reverse

from courses.forms import SectionForm
from courses.models import Section
from payment.models import PaymentTransaction
from tests.factories import (
    CourseFactory,
    RoomFactory,
    SectionFactory,
    SemesterFactory,
    StudentFactory,
)
from users.models import Profile


def build_instructor(course):
    """สร้างอาจารย์เพื่อใช้กับฟอร์ม"""
    profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        acdemic_title=Profile.AcademicTitle.LECTURER,
        department=course.department,
    )
    return profile.user

@pytest.mark.unit
@pytest.mark.django_db
def test_section_form_duplicate_same_course_semester_raises():
    """เทสนี้ฆ่า mutation เปลี่ยน == เป็น != ใน filter ตรวจเลขเซกชัน"""
    # Arrange
    course = CourseFactory()
    semester = SemesterFactory()
    room = RoomFactory()
    instructor = build_instructor(course)
    SectionFactory(course=course, semester=semester, section_number="1", room=room)
    data = {
        "semester": semester.pk,
        "section_number": "1",
        "room": room.pk,
        "capacity": 30,
        "instructors": [instructor.pk],
    }

    # Act
    form = SectionForm(data=data, course=course)

    # Assert
    assert form.is_valid() is False
    assert "section_number" in form.errors

@pytest.mark.unit
@pytest.mark.django_db
def test_section_form_same_number_different_course_is_valid():
    """เทสนี้ฆ่า mutation สลับ and/or ใน filter โดยตรวจว่าเคสอื่นต้องผ่าน"""
    # Arrange
    course_a = CourseFactory()
    course_b = CourseFactory(department=course_a.department)
    semester = SemesterFactory()
    room = RoomFactory()
    instructor_a = build_instructor(course_a)
    SectionFactory(course=course_a, semester=semester, section_number="2", room=room)

    data = {
        "semester": semester.pk,
        "section_number": "2",
        "room": room.pk,
        "capacity": 40,
        "instructors": [instructor_a.pk],
    }

    # Act
    form = SectionForm(data=data, course=course_b)

    # Assert
    assert form.is_valid()

@pytest.mark.unit
@pytest.mark.django_db
def test_enroll_section_blocks_existing_course_enrollment(client, student):
    """เทสนี้ฆ่า mutation ลืม not ในเงื่อนไขตรวจ course ซ้ำ"""
    # Arrange
    password = "TestPass123!"
    student.user.set_password(password)
    student.user.save()
    course = CourseFactory()
    section_existing = SectionFactory(course=course)
    section_new = SectionFactory(course=course)
    section_existing.students.add(student.user)
    client.login(username=student.user.username, password=password)

    # Act
    response = client.post(reverse("courses:enroll-section", args=[section_new.pk]), follow=True)

    # Assert
    assert response.status_code == 200
    assert section_new.students.count() == 0  # ไม่ถูกเพิ่มใหม่

@pytest.mark.unit
@pytest.mark.django_db
def test_enroll_section_blocks_duplicate_in_same_section(client, student):
    """เทสนี้ฆ่า mutation พลิก == กับ != ในการตรวจสมาชิกของเซกชัน"""
    # Arrange
    password = "TestPass123!"
    student.user.set_password(password)
    student.user.save()
    section = SectionFactory()
    section.students.add(student.user)
    client.login(username=student.user.username, password=password)

    # Act
    response = client.post(reverse("courses:enroll-section", args=[section.pk]), follow=True)

    # Assert
    assert response.status_code == 200
    assert section.students.count() == 1  # ยังมีแค่คนเดียว

@pytest.mark.unit
@pytest.mark.django_db
def test_enroll_section_free_course_skips_payment_block(client, student):
    """เทสนี้ฆ่า mutation เปลี่ยน > เป็น >= ในเงื่อนไขค่าเทอม"""
    # Arrange
    password = "TestPass123!"
    student.user.set_password(password)
    student.user.save()
    section = SectionFactory()
    section.course.fee = 0
    section.course.save()
    client.login(username=student.user.username, password=password)

    # Act
    response = client.post(reverse("courses:enroll-section", args=[section.pk]))

    # Assert
    assert response.status_code == 302
    assert student.user in section.students.all()
    assert PaymentTransaction.objects.filter(course=section.course, student=student).count() == 0
