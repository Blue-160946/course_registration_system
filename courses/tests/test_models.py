import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from courses.models import Course, Section, Semester, Room, Department, Faculty, Profile
from datetime import date

# --------------------
# Fixtures สำหรับการสร้างข้อมูลทดสอบ
# --------------------
@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="วิทยาศาสตร์")

@pytest.fixture
def department(db, faculty):
    return Department.objects.create(name="คอมพิวเตอร์", faculty=faculty)

@pytest.fixture
def course(db, department):
    return Course.objects.create(code="CS101", name="Programming", department=department, credits=3)

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
    return Group.objects.get_or_create(name='staff')[0]

@pytest.fixture
def instructor_group(db):
    return Group.objects.get_or_create(name='instructor')[0]

@pytest.fixture
def student_group(db):
    return Group.objects.get_or_create(name='student')[0]

@pytest.fixture
def staff_user(db, staff_group):
    user = User.objects.create_user(username="admin", password="123456789", is_staff=True)
    user.groups.add(staff_group)
    Profile.objects.create(user=user, user_type='ADMIN')
    return user

@pytest.fixture
def instructor_user(db, instructor_group):
    user = User.objects.create_user(username="instructor", password="pass123")
    user.groups.add(instructor_group)
    Profile.objects.create(user=user, user_type='INSTRUCTOR')
    return user

@pytest.fixture
def student_user(db, student_group):
    user = User.objects.create_user(username="student", password="pass123")
    user.groups.add(student_group)
    Profile.objects.create(user=user, user_type='STUDENT')
    return user

@pytest.fixture
def section(db, course, semester, room, instructor_user):
    s = Section.objects.create(
        course=course, section_number="1", semester=semester, room=room, capacity=2
    )
    s.instructors.add(instructor_user)
    return s

# --------------------
# Model Tests
# --------------------

@pytest.mark.django_db
def test_course_creation_positive(department):
    course_obj = Course.objects.create(code="CS201", name="Data Structures", department=department, credits=3)
    assert course_obj.code == "CS201"
    assert course_obj.name == "Data Structures"
    assert course_obj.department == department
    assert course_obj.credits == 3

@pytest.mark.django_db
def test_course_code_unique_negative(department):
    Course.objects.create(code="CS101", name="A", department=department, credits=3)
    with pytest.raises(IntegrityError):
        Course.objects.create(code="CS101", name="B", department=department, credits=3)

@pytest.mark.django_db
def test_course_credits_validation_negative(department):
    course = Course(code="CS102", name="A", department=department, credits=0)
    with pytest.raises(ValidationError):
        course.full_clean()

@pytest.mark.django_db
def test_section_creation_positive(course, semester, room):
    section = Section.objects.create(course=course, section_number="1", semester=semester, room=room, capacity=10)
    assert section.course == course
    assert section.section_number == "1"
    assert section.capacity == 10

@pytest.mark.django_db
def test_section_unique_constraint_negative(course, semester, room):
    Section.objects.create(course=course, section_number="1", semester=semester, room=room, capacity=10)
    with pytest.raises(IntegrityError):
        Section.objects.create(course=course, section_number="1", semester=semester, room=room, capacity=10)

@pytest.mark.django_db
def test_section_instructor_relationship_positive(section, instructor_user):
    assert section.instructors.count() == 1
    assert instructor_user in section.instructors.all()

@pytest.mark.django_db
def test_section_str_positive(section):
    # ปรับให้ตรงกับ __str__ ของ Section ใน model จริง
    assert str(section) == "CS101 - Section 1"

@pytest.mark.django_db
def test_course_delete_cascade_section(course, semester, room):
    section = Section.objects.create(course=course, section_number="1", semester=semester, room=room, capacity=10)
    course.delete()
    assert not Section.objects.filter(pk=section.pk).exists()

@pytest.mark.django_db
def test_semester_str_positive(semester):
    # ปรับให้ตรงกับ __str__ ของ Semester ใน model จริง
    assert str(semester) == f"ปีการศึกษา {semester.year} - ภาคเรียนที่ {semester.semester}"

@pytest.mark.django_db
def test_room_str_positive(room):
    # ปรับให้ตรงกับ __str__ ของ Room ใน model จริง
    assert str(room) == f"{room.building} - ห้อง {room.room_number}"

@pytest.mark.django_db
def test_department_str_positive(department):
    assert str(department) == department.name

# --------------------
# View Tests
# --------------------

@pytest.mark.django_db
def test_course_list_access_permissions(client, staff_user):
    url = reverse('courses:course-list')
    # (Negative) ไม่ล็อกอิน
    resp = client.get(url)
    assert resp.status_code == 302
    assert resp.url.startswith('/accounts/login/')

    # (Positive) staff เข้าถึงได้
    client.force_login(staff_user)
    resp = client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_section_create_view_positive(client, staff_user, course, semester, room, instructor_user):
    client.force_login(staff_user)
    url = reverse('courses:section-add', args=[course.id])
    data = {
        'section_number': '2',
        'semester': semester.id,
        'room': room.id,
        'capacity': 30,
        'instructors': [str(instructor_user.id)],
        'class_times-TOTAL_FORMS': 1,
        'class_times-INITIAL_FORMS': 0,
        'class_times-MIN_NUM_FORMS': 0,
        'class_times-MAX_NUM_FORMS': 1000,
        'class_times-0-day': 'MON',
        'class_times-0-start_time': '09:00',
        'class_times-0-end_time': '11:00',
    }
    resp = client.post(url, data)
    if resp.status_code == 200:
        print("SectionForm errors:", resp.context['form'].errors)
        print(resp.content.decode('utf-8'))
    assert resp.status_code == 302
    assert Section.objects.filter(course=course, section_number='2').exists()