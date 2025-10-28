from datetime import time
from types import SimpleNamespace

import pytest
from django.core.exceptions import ValidationError

from courses.models import Branch, ClassTime, Department, Faculty, Section
from tests.factories import (
    CourseFactory,
    RoomFactory,
    SectionFactory,
    SemesterFactory,
    StudentFactory,
)
from users.models import Profile

@pytest.mark.unit
@pytest.mark.django_db
def test_faculty_clean_rejects_blank_name():
    """ตรวจว่า Faculty.clean() ไม่อนุญาตให้ชื่อคณะว่าง"""
    faculty = Faculty(name="")

    with pytest.raises(ValidationError) as exc_info:
        faculty.full_clean()

    assert "name" in exc_info.value.error_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_department_clean_requires_faculty(monkeypatch):
    """ตรวจว่า Department.clean() ต้องมี faculty กำกับ (ใช้ monkeypatch จำลอง)"""
    department = Department(name="????????")
    monkeypatch.setattr(Department, "faculty", property(lambda self: None))

    with pytest.raises(ValidationError) as exc_info:
        department.clean()

    assert "faculty" in exc_info.value.error_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_branch_clean_name_too_short():
    """ตรวจว่า Branch.clean() ไม่อนุญาตชื่อสั้นกว่า 2 ตัวอักษร"""
    faculty = Faculty.objects.create(name="???????")
    department = Department.objects.create(name="???????", faculty=faculty)
    branch = Branch(name="?", department=department)

    with pytest.raises(ValidationError) as exc_info:
        branch.full_clean()

    assert "name" in exc_info.value.error_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_section_clean_requires_course():
    """ตรวจว่า Section.clean() ต้องมี course กำกับ มิฉะนั้นจะ error"""
    section = SectionFactory()
    section.course = None
    section.course_id = None

    with pytest.raises(ValidationError) as exc_info:
        section.clean()

    assert "course" in exc_info.value.error_dict


class DummyQuerySet(list):
    def exclude(self, **kwargs):
        pk_to_skip = kwargs.get("pk")
        return DummyQuerySet([obj for obj in self if obj.pk != pk_to_skip])


def _prepare_classtime_accessor(section):
    section.classtime_set = SimpleNamespace(all=lambda: list(section.class_times.all()))
    return section

@pytest.mark.unit
@pytest.mark.django_db
def test_section_clean_detects_room_overlap(monkeypatch):
    """ตรวจว่า Section.clean() ตรวจจับเวลาสอนชนกันในห้องเดียวกันได้"""
    semester = SemesterFactory()
    room = RoomFactory()
    course = CourseFactory()
    section_a = SectionFactory(course=course, semester=semester, room=room)
    ClassTime.objects.create(section=section_a, day="THU", start_time=time(9, 0), end_time=time(10, 0))

    section_b = SectionFactory(course=course, semester=semester, room=room)
    ClassTime.objects.create(section=section_b, day="THU", start_time=time(9, 30), end_time=time(10, 30))
    section_b.classtime_set = list(section_b.class_times.all())

    dummy_section = _prepare_classtime_accessor(section_a)
    monkeypatch.setattr(Section.objects, "filter", lambda **kwargs: DummyQuerySet([dummy_section]))

    with pytest.raises(ValidationError) as exc_info:
        section_b.clean()

    assert "????" in str(exc_info.value) or "Section" in str(exc_info.value)

@pytest.mark.unit
@pytest.mark.django_db
def test_section_clean_detects_instructor_overlap(monkeypatch):
    """ตรวจว่า Section.clean() ตรวจจับเวลาสอนชนกันของอาจารย์คนเดียวกันได้"""
    semester = SemesterFactory()
    course = CourseFactory()
    instructor_profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        department=course.department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    instructor = instructor_profile.user

    section_a = SectionFactory(course=course, semester=semester)
    section_a.instructors.add(instructor)
    ClassTime.objects.create(section=section_a, day="FRI", start_time=time(9, 0), end_time=time(10, 0))

    section_b = SectionFactory(course=course, semester=semester, room=RoomFactory())
    section_b.instructors.add(instructor)
    ClassTime.objects.create(section=section_b, day="FRI", start_time=time(9, 30), end_time=time(10, 30))
    section_b.classtime_set = list(section_b.class_times.all())

    dummy_section = _prepare_classtime_accessor(section_a)
    dummy_section.room = RoomFactory()
    monkeypatch.setattr(Section.objects, "filter", lambda **kwargs: DummyQuerySet([dummy_section]))

    with pytest.raises(ValidationError) as exc_info:
        section_b.clean()

    assert "non_field_errors" in exc_info.value.error_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_classtime_clean_detects_conflicts():
    """ตรวจว่า ClassTime.clean() ตรวจสอบเวลาซ้อนของห้องและอาจารย์ได้"""
    semester = SemesterFactory()
    instructor_profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        department=CourseFactory().department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    instructor = instructor_profile.user

    section_a = SectionFactory(semester=semester)
    section_a.instructors.add(instructor)
    ClassTime.objects.create(section=section_a, day="MON", start_time=time(9, 0), end_time=time(10, 0))

    section_b = SectionFactory(semester=semester, room=section_a.room)
    section_b.instructors.add(instructor)
    classtime = ClassTime(section=section_b, day="MON", start_time=time(9, 30), end_time=time(10, 30))

    with pytest.raises(ValidationError):
        classtime.clean()


# Profile validations

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_student_requires_branch():
    profile = StudentFactory()
    profile.branch = None

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean()

    assert "branch" in exc_info.value.error_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_student_disallows_academic_title():
    profile = StudentFactory()
    profile.acdemic_title = Profile.AcademicTitle.LECTURER

    with pytest.raises(ValidationError):
        profile.full_clean()

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_instructor_requires_department():
    profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        department=None,
        acdemic_title=None,
    )
    profile.address = "???????????????????????????"

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean()

    assert "department" in exc_info.value.error_dict

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_instructor_rejects_student_fields():
    profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id="66000000",
        branch=None,
        student_status=Profile.StudentStatus.STUDYING,
        department=CourseFactory().department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    profile.address = "???????????????????????????"

    with pytest.raises(ValidationError):
        profile.full_clean()

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_staff_rejects_student_fields():
    profile = StudentFactory()
    profile.user_type = Profile.UserType.STAFF
    profile.job_title = None

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean()

    assert "job_title" in exc_info.value.error_dict

    profile.job_title = Profile.JobTitle.REGISTRATION_OFFICER
    profile.student_id = "66000000"

    with pytest.raises(ValidationError):
        profile.full_clean()

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_names_must_be_pair():
    profile = StudentFactory()
    profile.first_name_th = "?????"
    profile.last_name_th = ""

    with pytest.raises(ValidationError):
        profile.full_clean()

@pytest.mark.unit
@pytest.mark.django_db
def test_profile_address_min_length():
    profile = StudentFactory()
    profile.address = "????"

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean()

    assert "address" in exc_info.value.error_dict
