import pytest

from courses.forms import (
    ClassTimeForm,
    CourseForm,
    InstructorChoiceField,
    SectionForm,
)
from courses.models import ClassTime, Section
from tests.factories import (
    CourseFactory,
    RoomFactory,
    SectionFactory,
    SemesterFactory,
    StudentFactory,
    UserFactory,
)
from users.models import Profile

@pytest.mark.unit
@pytest.mark.django_db
def test_instructor_choice_field_label_uses_full_name():
    """ตรวจ label ของ InstructorChoiceField เมื่อมีชื่อ-นามสกุลไทย"""
    instructor = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        department=CourseFactory().department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    ).user
    instructor.profile.first_name_th = "สมชาย"
    instructor.profile.last_name_th = "ใจดี"
    instructor.profile.save()

    field = InstructorChoiceField(queryset=Profile.objects.none())

    label = field.label_from_instance(instructor)

    assert "สมชาย ใจดี" in label

@pytest.mark.unit
@pytest.mark.django_db
def test_instructor_choice_field_label_falls_back_to_username():
    """ตรวจว่าไม่มีชื่อไทยแล้ว fallback เป็น username"""
    user = UserFactory(username="plain_user")
    field = InstructorChoiceField(queryset=Profile.objects.none())

    label = field.label_from_instance(user)

    assert label == "plain_user"

@pytest.mark.unit
@pytest.mark.django_db
def test_course_form_assigns_widget_classes_except_checkbox():
    """ตรวจ CourseForm ใส่ class form-control ทุก field ยกเว้น Checkbox"""
    form = CourseForm()

    assert form.fields["code"].widget.attrs["class"] == "form-control"
    assert form.fields["is_active"].widget.attrs["class"] == "form-check-input"


def _make_instructor(department):
    profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        department=department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    profile.first_name_th = ""
    profile.last_name_th = ""
    profile.address = "ที่อยู่อย่างน้อยสิบตัวอักษร"
    profile.save()
    return profile.user

@pytest.mark.unit
@pytest.mark.django_db
def test_section_form_clean_returns_when_course_missing():
    """ตรวจว่า SectionForm.clean ข้าม validation เมื่อตั้งค่า course=None"""
    course = CourseFactory()
    room = RoomFactory()
    instructor = _make_instructor(course.department)
    form = SectionForm(
        data={
            "semester": SemesterFactory().pk,
            "section_number": "3",
            "room": room.pk,
            "capacity": 25,
            "instructors": [instructor.pk],
        },
        course=None,
    )

    assert form.is_valid()

@pytest.mark.unit
@pytest.mark.django_db
def test_section_form_clean_excludes_current_instance():
    """ตรวจว่าการแก้ไขเซกชันเดิมไม่เจอเลขซ้ำ"""
    section = SectionFactory(section_number="7")
    instructor = _make_instructor(section.course.department)
    form = SectionForm(
        data={
            "semester": section.semester.pk,
            "section_number": "7",
            "room": section.room.pk,
            "capacity": section.capacity,
            "instructors": [instructor.pk],
        },
        course=section.course,
        instance=section,
    )

    assert form.is_valid()

@pytest.mark.unit
@pytest.mark.django_db
def test_class_time_form_clean_returns_when_section_missing():
    """ตรวจว่าไม่มี section แล้ว clean คืนค่าได้โดยไม่เพิ่ม error"""
    form = ClassTimeForm(
        data={"day": "MON", "start_time": "09:00", "end_time": "10:00"},
        section=None,
    )

    assert form.is_valid()

@pytest.mark.unit
@pytest.mark.django_db
def test_class_time_form_clean_detects_adjacent_overlap():
    """ตรวจกรณีเวลาเป๊ะต่อกัน (==) ว่าถูกแจ้งเตือน"""
    section = SectionFactory()
    ClassTime.objects.create(
        section=section, day="TUE", start_time="09:00", end_time="10:00"
    )
    form = ClassTimeForm(
        data={"day": "TUE", "start_time": "10:00", "end_time": "11:00"},
        section=section,
    )

    assert not form.is_valid()
    assert form.non_field_errors()

@pytest.mark.unit
@pytest.mark.django_db
def test_class_time_form_clean_detects_instructor_overlap():
    """ตรวจกรณีอาจารย์ซ้ำข้ามเซกชันเดียวกัน"""
    semester = SemesterFactory()
    instructor_profile = StudentFactory(
        user_type=Profile.UserType.INSTRUCTOR,
        student_id=None,
        branch=None,
        student_status=None,
        department=CourseFactory().department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    instructor_user = instructor_profile.user
    section_a = SectionFactory(semester=semester)
    section_a.instructors.add(instructor_user)
    ClassTime.objects.create(
        section=section_a, day="WED", start_time="09:00", end_time="10:00"
    )

    section_b = SectionFactory(semester=semester)
    section_b.instructors.add(instructor_user)
    form = ClassTimeForm(
        data={"day": "WED", "start_time": "09:30", "end_time": "10:30"},
        section=section_b,
    )

    assert not form.is_valid()
    assert any("อาจารย์" in msg or "Instructor" in msg for msg in form.non_field_errors())

