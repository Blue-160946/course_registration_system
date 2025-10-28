import re
import pytest
from datetime import date, time
from django.urls import reverse
from django.http import HttpRequest
from django.utils import timezone
from users.models import User, Profile
from courses.models import Semester, Course, Section, Room, ClassTime, Faculty, Department
from courses.views import my_schedule_pdf

@pytest.mark.django_db
def test_my_schedule_pdf_unit(monkeypatch):
    # 1. สร้าง user + profile
    user = User.objects.create_user(username="student1", password="pass1234")
    profile = Profile.objects.create(
        user=user,
        user_type=Profile.UserType.STUDENT,
        student_id="00000001"
    )

    # 2. สร้าง semester
    semester = Semester.objects.create(
        year=2568,
        semester=1,
        start_date=date(2025, 9, 1),
        end_date=date(2026, 2, 28)
    )

    # 3. สร้าง request mock
    request = HttpRequest()
    request.user = user

    # 4. patch timezone.now() ให้ deterministic
    monkeypatch.setattr(timezone, 'now', lambda: timezone.datetime(2025, 9, 27))

    # 5. เรียกฟังก์ชัน
    response = my_schedule_pdf(request)

    # 6. ตรวจสอบ response
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    # ✅ ใช้ regex ให้ยืดหยุ่น
    assert re.match(r'attachment; filename="schedule_.*\.pdf"', response['Content-Disposition'])


@pytest.mark.django_db
def test_my_schedule_pdf_integration(client):
    # 1. สร้าง Faculty และ Department
    faculty = Faculty.objects.create(name="คณะวิทยาศาสตร์")
    department = Department.objects.create(name="วิทยาการคอมพิวเตอร์", faculty=faculty)

    # 2. สร้าง user + profile
    user = User.objects.create_user(username="student2", password="pass1234")
    profile = Profile.objects.create(
        user=user,
        user_type=Profile.UserType.STUDENT,
        student_id="12345678"
    )

    # 3. สร้าง semester
    semester = Semester.objects.create(
        year=2568,
        semester=1,
        start_date=date(2025, 9, 1),
        end_date=date(2026, 2, 28)
    )

    # 4. สร้าง course, section, room, class_time
    course = Course.objects.create(
        code="123456",
        name="วิชา Test",
        credits=3,
        department=department
    )

    room = Room.objects.create(building="ตึก A", room_number="101")

    section = Section.objects.create(
        course=course,
        section_number="1",
        capacity=30,
        semester=semester,
        room=room
    )
    section.students.add(user)

    ClassTime.objects.create(
        section=section,
        day="MON",
        start_time=time(9, 0),
        end_time=time(11, 0)
    )

    # 5. login
    client.login(username="student2", password="pass1234")

    # 6. เรียก view PDF โดยใช้ reverse() ถูกต้อง
    url = reverse('courses:my-schedule-pdf')
    response = client.get(url)

    # 7. ตรวจสอบ response
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert re.match(r'attachment; filename="schedule_.*\.pdf"', response['Content-Disposition'])
