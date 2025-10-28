# courses/tests/test_Section_unit.py
import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from datetime import date

from courses.models import Faculty, Department, Course, Semester, Room, Section, Profile

# ---------- Fixtures ขั้นต่ำ ----------
@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="วิทยาศาสตร์")

@pytest.fixture
def department(db, faculty):
    return Department.objects.create(name="คอมพิวเตอร์", faculty=faculty)

@pytest.fixture
def course(db, department):
    return Course.objects.create(code="123456", name="Programming",
                                 department=department, credits=3, is_active=True)

@pytest.fixture
def semester(db):
    return Semester.objects.create(year=2567, semester=1,
                                   start_date=date(2024, 8, 1),
                                   end_date=date(2024, 12, 31))

@pytest.fixture
def room_a(db):
    return Room.objects.create(building="A", room_number="101")

@pytest.fixture
def instructor_group(db):
    return Group.objects.get_or_create(name="instructor")[0]

@pytest.fixture
def instructor(db, instructor_group):
    u = User.objects.create_user(username="instructor", password="x")
    u.groups.add(instructor_group)
    Profile.objects.create(user=u, user_type="INSTRUCTOR")
    return u


# ===================== TC-046: สร้าง Section ด้วยข้อมูลถูกต้อง =====================
@pytest.mark.django_db
def test_TC_046_create_section_valid(course, semester, room_a, instructor):
    s = Section(course=course, semester=semester, room=room_a,
                section_number="1", capacity=30)
    s.save()              
    s.full_clean()       
    s.instructors.add(instructor)
    assert Section.objects.filter(pk=s.pk).exists()

# ===================== TC-047: duplicate =====================
@pytest.mark.django_db
def test_TC_047_disallow_duplicate_section_number(course, semester, room_a):
    Section.objects.create(course=course, semester=semester, room=room_a,
                           section_number="1", capacity=30)
    # สร้างอีกตัวให้ "ไม่ซ้ำ" ก่อน → save → แก้ให้ซ้ำ → full_clean
    dup = Section(course=course, semester=semester, room=room_a,
                  section_number="2", capacity=30)
    dup.save()
    dup.section_number = "1"  # ทำให้ซ้ำ (รายวิชา+ภาคเรียนเดียวกัน)
    with pytest.raises(ValidationError):
        dup.full_clean()

# ===================== TC-048: จำนวนที่นั่ง = 0 =====================
@pytest.mark.django_db
def test_TC_048_capacity_zero_invalid(course, semester, room_a):
    s = Section(course=course, semester=semester, room=room_a,
                section_number="1", capacity=30)
    s.save()
    s.capacity = 0
    with pytest.raises(ValidationError):
        s.full_clean()

# ===================== TC-049: จำนวนที่นั่ง แบบไม่ถูกต้อง =====================
@pytest.mark.django_db
def test_TC_049_capacity_negative_invalid(course, semester, room_a):
    s = Section(course=course, semester=semester, room=room_a,
                section_number="1", capacity=30)
    s.save()
    s.capacity = -1
    with pytest.raises(ValidationError):
        s.full_clean()

# ===================== TC-050: จำนวนที่นั่ง ไม่ใช่ตัวเลข =====================
@pytest.mark.django_db
def test_TC_050_capacity_not_a_number_invalid(course, semester, room_a):
    from courses.forms import SectionForm

    # 1) สร้าง Section 
    s = Section.objects.create(
        course=course, semester=semester, room=room_a,
        section_number="X", capacity=30
    )

    # 2) ส่งค่าที่ผิดเข้า form 
    form = SectionForm(data={
        "semester": semester.id,
        "section_number": "1",
        "room": room_a.id,
        "capacity": "abc",   # ไม่ใช่ตัวเลข
        "instructors": [],
    }, instance=s)

    # 3) ฟอร์มต้อง invalid และฟ้องที่ capacity
    assert not form.is_valid(), f"ควร invalid แต่กลับ valid: errors={form.errors}"
    assert "capacity" in form.errors

# ===================== TC-051: ไม่เลือกเทอม (semester) =====================
@pytest.mark.django_db
def test_TC_051_missing_semester_invalid(course, room_a):
    s = Section(course=course, semester=None, room=room_a,
                section_number="1", capacity=30)
    # ให้มี pk ก่อนแล้วค่อยทำให้ invalid
    s.semester = Semester.objects.create(year=2567, semester=2,
                                         start_date=date(2025, 1, 1),
                                         end_date=date(2025, 5, 1))
    s.save()
    s.semester = None
    with pytest.raises(ValidationError) as e:
        s.full_clean()
    assert "semester" in e.value.message_dict

# ===================== TC-052: ไม่เลือกห้อง (room) =====================
@pytest.mark.django_db
def test_TC_052_missing_room_invalid(course, semester, room_a):
    from courses.forms import SectionForm

    # 1) สร้าง Section ที่ valid และ save ให้มี pk ก่อน
    s = Section.objects.create(
        course=course, semester=semester, room=room_a,
        section_number="X", capacity=30
    )

    # 2) ส่ง room ว่างเข้า form โดยยังผูก instance เดิม
    form = SectionForm(data={
        "semester": semester.id,
        "section_number": "1",
        "room": "",          # ไม่เลือกห้อง
        "capacity": 30,
        "instructors": [],
    }, instance=s)

    # 3) ฟอร์มต้อง invalid และฟ้องที่ room
    assert not form.is_valid(), f"ควร invalid แต่กลับ valid: errors={form.errors}"
    assert "room" in form.errors

# ===================== TC-053: ไม่เลือกผู้สอน =====================
@pytest.mark.django_db
def test_TC_053_instructors_required_on_form(semester, room_a):
    try:
        from courses.forms import SectionForm
    except Exception:
        pytest.skip("ไม่มี SectionForm / ระบบไม่บังคับผู้สอนในฟอร์ม")

    form = SectionForm(data={
        "semester": semester.id,
        "section_number": "1",
        "room": room_a.id,
        "capacity": 30,
        "instructors": [],  # ไม่เลือกผู้สอน
    })
    assert not form.is_valid()
    assert "instructors" in form.errors

# ===================== TC-054: แก้ไขเลข Section ให้ไปชนของเดิม =====================
@pytest.mark.django_db
def test_TC_054_update_to_duplicate_is_disallowed(course, semester, room_a):
    Section.objects.create(course=course, semester=semester, room=room_a,
                           section_number="1", capacity=30)
    b = Section.objects.create(course=course, semester=semester, room=room_a,
                               section_number="2", capacity=30)
    b.section_number = "1"  # ทำให้ซ้ำ
    with pytest.raises(ValidationError):
        b.full_clean()

# ===================== TC-055: แก้ไขจำนวนที่นั่งสำเร็จ =====================
@pytest.mark.django_db
def test_TC_055_update_capacity_success(course, semester, room_a, instructor):
    s = Section.objects.create(course=course, semester=semester, room=room_a,
                               section_number="1", capacity=30)
    s.instructors.add(instructor)
    s.capacity = 40
    s.full_clean()  # ไม่ควร raise
    s.save()
    s.refresh_from_db()
    assert s.capacity == 40

# ===================== TC-056: update to same section number is allowed =====================
@pytest.mark.django_db
def test_TC_056_update_to_same_section_number_is_allowed(course, semester, room_a):
    s = Section.objects.create(course=course, semester=semester, room=room_a,
                               section_number="1", capacity=30)
    s.section_number = "1"  # ไม่เปลี่ยนแปลง
    s.full_clean()  # ไม่ควร raise   
    s.save()
    s.refresh_from_db()
    assert s.section_number == "1"

# ===================== TC-057: update to different section number is allowed =====================
@pytest.mark.django_db
def test_TC_057_update_to_different_section_number_is_allowed(course, semester, room_a):
    s = Section.objects.create(course=course, semester=semester, room=room_a,
                               section_number="1", capacity=30)
    s.section_number = "2"  # เปลี่ยนแปลงเป็นหมายเลขกลุ่มใหม่
    s.full_clean()  # ไม่ควร raise   
    s.save()
    s.refresh_from_db()
    assert s.section_number == "2"

# ===================== TC-058: ย้ายไป “คนละภาคเรียน” แล้ว ใช้เลขเดิม → ต้องอนุญาต =====================
@pytest.mark.django_db
def test_TC_058_update_to_same_section_number_in_different_semester_is_allowed(course, semester, room_a):
    s = Section.objects.create(course=course, semester=semester, room=room_a,
                               section_number="1", capacity=30)
    new_semester = Semester.objects.create(year=2568, semester=1,
                                           start_date=date(2025, 8, 1),
                                           end_date=date(2025, 12, 31))
    s.semester = new_semester
    s.section_number = "1"  # เปลี่ยนแปลงเป็นหมายเลขกลุ่มใหม่ในเทอมใหม่
    s.full_clean()  # ไม่ควร raise
    s.save()
    s.refresh_from_db()
    assert s.section_number == "1"
    assert s.semester == new_semester

# ===================== TC-059: ย้ายไป “คนละภาคเรียน” แล้ว เปลี่ยนเป็นเลขใหม่ =====================
@pytest.mark.django_db
def test_TC_059_update_to_different_section_number_in_different_semester_is_allowed(course, semester, room_a):
    # มี Section เริ่มต้นในเทอมเดิม
    s = Section.objects.create(course=course, semester=semester, room=room_a,
                               section_number="1", capacity=30)

    # เทอมใหม่ (ไม่มีชน)
    new_semester = Semester.objects.create(
        year=2568, semester=1,
        start_date=date(2025, 8, 1), end_date=date(2025, 12, 31)
    )

    # (กันชน) ยืนยันว่าไม่มีใครใช้เลข "2" ในเทอมใหม่อยู่ก่อน
    assert not Section.objects.filter(course=course, semester=new_semester, section_number="2").exists()

    # แก้เทอม + เปลี่ยนเลขกลุ่ม
    s.semester = new_semester
    s.section_number = "2"

    # ไม่ควร raise เพราะคนละเทอมและเลขใหม่ไม่ชน
    s.full_clean()
    s.save()
    s.refresh_from_db()

    assert s.section_number == "2"
    assert s.semester == new_semester