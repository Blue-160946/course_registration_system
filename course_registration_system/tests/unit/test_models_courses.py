from datetime import date, datetime, time

import pytest
from django.core.exceptions import ValidationError

from courses.models import (
    Branch,
    ClassTime,
    Course,
    Department,
    Faculty,
    Room,
    Section,
    Semester,
)
from tests import factories
from users.models import Profile


class _FakeManager(list):
    """ตัวช่วยให้ list มีเมธอด all() เหมือน RelatedManager"""

    def all(self):
        return list(self)


@pytest.mark.unit
@pytest.mark.django_db
def test_faculty_clean_rejects_short_name():
    # Arrange: เตรียม Faculty ที่ชื่อสั้นเกินไป
    faculty = Faculty(name="ก")

    # Act + Assert: เรียก clean แล้วต้องยิง ValidationError ที่ field name
    with pytest.raises(ValidationError) as exc:
        faculty.clean()
    assert "name" in exc.value.message_dict


def test_faculty_str_returns_name():
    # Arrange: สร้าง Faculty ที่มีชื่อสมบูรณ์
    faculty = Faculty(name="คณะทดสอบ")

    # Act: แปลงเป็นสตริง
    rendered = str(faculty)

    # Assert: ต้องได้ชื่อเดิมกลับมา
    assert rendered == "คณะทดสอบ"


@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "mutator,expected_field",
    [
        (lambda dept: setattr(dept, "name", ""), "name"),
        (lambda dept: setattr(dept, "name", "ก"), "name"),
        (lambda dept: setattr(dept, "faculty", None), "faculty"),
    ],
)
def test_department_clean_required_fields(mutator, expected_field):
    # Arrange: เตรียม Department ถูกต้องก่อน
    department = Department(name="ภาควิชาทดสอบ", faculty=factories.FacultyFactory())
    mutator(department)

    # Act + Assert: เรียก clean แล้วต้องระบุ field ที่ผิด
    with pytest.raises(ValidationError) as exc:
        department.clean()
    assert expected_field in exc.value.message_dict


@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "mutator,expected_field",
    [
        (lambda branch: setattr(branch, "name", ""), "name"),
        (lambda branch: setattr(branch, "name", "ก"), "name"),
        (lambda branch: setattr(branch, "department", None), "department"),
    ],
)
def test_branch_clean_required_fields(mutator, expected_field):
    # Arrange: เตรียม Branch สมบูรณ์
    branch = Branch(name="สาขาทดสอบ", department=factories.DepartmentFactory())
    mutator(branch)

    # Act + Assert: ตรวจสอบ clean ว่าต้องโยน ValidationError จุดที่คาด
    with pytest.raises(ValidationError) as exc:
        branch.clean()
    assert expected_field in exc.value.message_dict
    
    
@pytest.mark.unit
@pytest.mark.django_db
def test_branch_str_returns_name():
    # Arrange: สร้าง Branch ที่มีชื่อ
    branch = Branch(name="สาขาตัวอย่าง", department=factories.DepartmentFactory())

    # Act: แปลงเป็นสตริง
    rendered = str(branch)

    # Assert: ต้องได้ชื่อกลับมาตรง ๆ
    assert rendered == "สาขาตัวอย่าง"


@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "missing_field",
    ["year", "semester", "start_date", "end_date"],
)
def test_semester_clean_requires_core_fields(missing_field):
    # Arrange: สร้าง Semester ที่เว้น field หนึ่งไว้
    semester = Semester(
        year=2567,
        semester=1,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 7, 1),
    )
    setattr(semester, missing_field, None)

    # Act + Assert: เรียก clean แล้วต้องระบุ field ที่หาย
    with pytest.raises(ValidationError) as exc:
        semester.clean()
    assert missing_field in exc.value.message_dict


@pytest.mark.unit
@pytest.mark.django_db
def test_semester_clean_blocks_far_future_year():
    # Arrange: ตั้งปีการศึกษาล่วงหน้าเกิน 1 ปี
    current_be_year = datetime.now().year + 543
    semester = Semester(
        year=current_be_year + 2,
        semester=1,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 8, 1),
    )

    # Act + Assert: เรียก clean แล้วต้องเจอ ValidationError ที่ year
    with pytest.raises(ValidationError) as exc:
        semester.clean()
    assert "year" in exc.value.message_dict


@pytest.mark.unit
@pytest.mark.django_db
def test_semester_clean_rejects_end_before_start():
    # Arrange: กำหนด end_date ให้น้อยกว่า start_date
    semester = Semester(
        year=2567,
        semester=1,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 5, 1),
    )

    # Act + Assert: ต้องเจอ ValidationError ที่ end_date
    with pytest.raises(ValidationError) as exc:
        semester.clean()
    assert "end_date" in exc.value.message_dict


@pytest.mark.unit
@pytest.mark.django_db
def test_semester_clean_rejects_too_short_duration():
    # Arrange: ตั้งคาบเวลาสั้นกว่า 180 วัน
    semester = Semester(
        year=2567,
        semester=1,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 1),
    )

    # Act + Assert: แจ้งเตือนว่าระยะเวลาสั้นเกินไป
    with pytest.raises(ValidationError) as exc:
        semester.clean()
    assert any("180" in message for message in exc.value.messages)


@pytest.mark.unit
@pytest.mark.django_db
@pytest.mark.parametrize(
    "mutator,expected_field",
    [
        (lambda room: setattr(room, "building", ""), "building"),
        (lambda room: setattr(room, "room_number", ""), "room_number"),
        (lambda room: setattr(room, "building", "ก"), "building"),
        (lambda room: setattr(room, "room_number", " "), "room_number"),
    ],
)
def test_room_clean_validation(mutator, expected_field):
    # Arrange: เตรียม Room สมบูรณ์แล้วแก้ไขค่า
    room = Room(building="อาคารเอ", room_number="101")
    mutator(room)

    # Act + Assert: เรียก clean แล้วต้องฟ้อง field ที่ผิด
    with pytest.raises(ValidationError) as exc:
        room.clean()
    assert expected_field in exc.value.message_dict
    
    
@pytest.mark.unit
@pytest.mark.django_db
def test_course_str_renders_code_and_name():
    # Arrange: ใช้ข้อมูลคงที่เพื่อเช็ค __str__
    course = Course(code="123456", name="Software Testing", department=factories.DepartmentFactory())

    # Act: เรียก str()
    rendered = str(course)

    # Assert: ควรได้รูปแบบ "รหัส - ชื่อ"
    assert rendered == "123456 - Software Testing"


# @pytest.mark.django_db
# def test_section_clean_detects_room_conflict():
#     # Arrange: สร้าง Section สองกลุ่มในห้องเดียวกันที่เวลาชนกัน
#     section_a = factories.SectionFactory()
#     section_b = factories.SectionFactory(
#         course=section_a.course,
#         semester=section_a.semester,
#         room=section_a.room,
#     )
#     ct_a = ClassTime.objects.create(
#         section=section_a,
#         day="MON",
#         start_time=time(9, 0),
#         end_time=time(10, 0),
#     )
#     ClassTime.objects.create(
#         section=section_b,
#         day="MON",
#         start_time=time(9, 30),
#         end_time=time(10, 30),
#     )
#     section_a.classtime = _FakeManager([ct_a])
#     section_b.classtime = _FakeManager(section_b.class_times.all())

#     # Act + Assert: เรียก clean แล้วต้องแจ้งว่าห้องชนกัน
#     with pytest.raises(ValidationError) as exc:
#         section_a.clean()
#     assert "ห้อง" in str(exc.value)


@pytest.mark.unit
@pytest.mark.django_db
def test_class_time_clean_blocks_room_overlap():
    # Arrange: มี ClassTime ของอีก Section ในห้องเดียวกันช่วงเวลาเหลื่อม
    section_a = factories.SectionFactory()
    section_b = factories.SectionFactory(
        course=section_a.course,
        semester=section_a.semester,
        room=section_a.room,
    )
    ClassTime.objects.create(
        section=section_b,
        day="TUE",
        start_time=time(10, 0),
        end_time=time(11, 0),
    )
    target = ClassTime(
        section=section_a,
        day="TUE",
        start_time=time(10, 30),
        end_time=time(11, 30),
    )

    # Act + Assert: เรียก clean แล้วต้องฟ้องเรื่องห้องซ้ำ
    with pytest.raises(ValidationError) as exc:
        target.clean()
    assert "ห้อง" in str(exc.value)


@pytest.mark.unit
@pytest.mark.django_db
def test_class_time_clean_blocks_instructor_overlap():
    # Arrange: สร้างสอง Section คนละห้องแต่ใช้อาจารย์เดียวกันและเวลาทับ
    section_a = factories.SectionFactory()
    section_b = factories.SectionFactory(semester=section_a.semester)
    instructor_user = factories.UserFactory()
    Profile.objects.create(
        user=instructor_user,
        user_type=Profile.UserType.INSTRUCTOR,
        department=section_a.course.department,
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )
    section_a.instructors.add(instructor_user)
    section_b.instructors.add(instructor_user)
    ClassTime.objects.create(
        section=section_b,
        day="WED",
        start_time=time(13, 0),
        end_time=time(14, 0),
    )
    target = ClassTime(
        section=section_a,
        day="WED",
        start_time=time(13, 30),
        end_time=time(14, 30),
    )

    # Act + Assert: ควรแจ้งเตือนว่าอาจารย์ชนตาราง
    with pytest.raises(ValidationError) as exc:
        target.clean()
    assert "อาจารย์" in str(exc.value)
