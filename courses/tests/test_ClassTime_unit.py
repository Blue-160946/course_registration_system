# courses/tests/test_ClassTime.py
import pytest
from datetime import date, time

from django.contrib.auth.models import User, Group
from django.urls import reverse, NoReverseMatch

from courses.models import (
    Faculty, Department, Course, Semester, Room, Section, ClassTime, Profile
)
from courses.forms import ClassTimeForm

# -------------------------------------------------------------------
# URL names 
# -------------------------------------------------------------------
URL_CT_ADD    = "courses:time-add"     # args=[section.id]
URL_CT_EDIT   = "courses:time-edit"    # args=[ct.id]
URL_CT_DELETE = "courses:time-delete"  # args=[ct.id]

CT_ADD_NAMES = ["courses:time-add"]
CT_EDIT_NAMES = ["courses:time-edit"]
CT_DELETE_NAMES = ["courses:time-delete"]

# ----------------
# URL helpers
# ----------------
def _reverse_first(candidates, args):
    for name in candidates:
        try:
            return reverse(name, args=args)
        except NoReverseMatch:
            continue
    pytest.skip(f"ไม่พบ URL name ใดเลยใน {candidates}\n→ โปรดแก้รายชื่อให้ตรงกับ urls.py ของคุณ")

def _url_ct_add(section):
    return _reverse_first(CT_ADD_NAMES, [section.id])

def _url_ct_edit(ct):
    return _reverse_first(CT_EDIT_NAMES, [ct.id])

def _url_ct_delete(ct):
    return _reverse_first(CT_DELETE_NAMES, [ct.id])

# ----------------
# Fixtures พื้นฐาน
# ----------------
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
    return Semester.objects.create(
        year=2567, semester=1,
        start_date=date(2024, 8, 1), end_date=date(2024, 12, 31)
    )

@pytest.fixture
def semester_next(db):
    return Semester.objects.create(
        year=2568, semester=1,
        start_date=date(2025, 8, 1), end_date=date(2025, 12, 31)
    )

@pytest.fixture
def room_a(db):
    return Room.objects.create(building="A", room_number="101")  # A-101

@pytest.fixture
def room_b(db):
    return Room.objects.create(building="B", room_number="201")  # B-201

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
    u = User.objects.create_user(username="admin", password="pass123", is_staff=True)
    u.groups.add(staff_group)
    Profile.objects.create(user=u, user_type="ADMIN")
    return u

@pytest.fixture
def instructor_user(db, instructor_group):
    u = User.objects.create_user(username="instructor", password="pass123")
    u.groups.add(instructor_group)
    Profile.objects.create(user=u, user_type="INSTRUCTOR")
    return u

@pytest.fixture
def student_user(db, student_group):
    u = User.objects.create_user(username="student1", password="pass123")
    u.groups.add(student_group)
    Profile.objects.create(user=u, user_type="STUDENT")
    return u

@pytest.fixture
def section(db, course, semester, room_a, instructor_user):
    s = Section.objects.create(
        course=course, semester=semester, room=room_a, section_number="1", capacity=30
    )
    s.instructors.add(instructor_user)
    return s

# ----------------
# Helpers
# ----------------
def _login_staff(client, user):
    client.force_login(user)

def _payload_add(day, start_hhmm, end_hhmm):
    # ปรับชื่อ key ให้ตรงกับฟอร์มเพิ่มคาบเรียนของคุณ หากต่างจากนี้
    return {"day": day, "start_time": start_hhmm, "end_time": end_hhmm}


# =========================================================
#                    UNIT TESTS
#                  (ตาม TC-068 ถึง TC-077)
# =========================================================

class ValidationError(Exception):
    def __init__(self, msg, code=None):
        super().__init__(msg)
        self.code = code

def end_after_start(start, end):
    if end <= start:
        raise ValidationError("end <= start", code="end_le_start")
    return True

def overlaps(start1, end1, start2, end2, inclusive=True):
    if inclusive:
        return not (end1 <= start2 or end2 <= start1)
    else:
        return not (end1 < start2 or end2 < start1)

def has_section_conflict(existing, new):
    # existing: list of dicts
    for e in existing:
        if e['section'] == new['section'] and e['day'] == new['day']:
            if overlaps(e['start'], e['end'], new['start'], new['end']):
                return True
    return False

def has_room_conflict(existing, new):
    for e in existing:
        if e['room'] == new['room'] and e['semester'] == new['semester'] and e['day'] == new['day']:
            if overlaps(e['start'], e['end'], new['start'], new['end']):
                return True
    return False

def has_instructor_conflict(existing, new):
    for e in existing:
        if e['semester'] == new['semester'] and e['day'] == new['day']:
            if set(e['instructors']) & set(new['instructors']):
                if overlaps(e['start'], e['end'], new['start'], new['end']):
                    return True
    return False

# TC-068: เพิ่มคาบเรียนสำเร็จ (ไม่มีคาบใน existing)
def test_TC_068_add_class_time_success():
    existing = []
    new = dict(section=1, semester=100, room=10, day="MON", start=time(9,0), end=time(11,0), instructors=[7])
    # 1) end_after_start
    assert end_after_start(new['start'], new['end']) is True
    # 2) ไม่มี conflict
    assert not has_section_conflict(existing, new)
    assert not has_room_conflict(existing, new)
    assert not has_instructor_conflict(existing, new)

# TC-069: end <= start ต้องไม่ผ่าน
def test_TC_069_end_le_start_invalid():
    with pytest.raises(ValidationError) as e:
        end_after_start(time(11,0), time(9,0))
    assert e.value.code == "end_le_start"

# TC-070: ทับซ้อนใน Section เดียวกัน
def test_TC_070_overlap_same_section():
    existing = [
        dict(section=1, semester=100, room=10, day="MON", start=time(9,0), end=time(11,0), instructors=[7])
    ]
    new = dict(section=1, semester=100, room=10, day="MON", start=time(10,0), end=time(12,0), instructors=[7])
    assert has_section_conflict(existing, new) is True

# TC-071: แก้ไขเวลาแล้วไม่ทับซ้อน
def test_TC_071_edit_time_no_conflict():
    existing = [
        dict(section=1, semester=100, room=10, day="MON", start=time(9,0), end=time(11,0), instructors=[7])
    ]
    edited = dict(section=1, semester=100, room=10, day="MON", start=time(12,0), end=time(14,0), instructors=[7])
    assert end_after_start(edited['start'], edited['end']) is True
    assert not has_section_conflict(existing, edited)

# TC-073: ทับซ้อนเพราะ “ห้องเดียวกัน” ในเทอมเดียวกัน
def test_TC_073_room_conflict():
    existing = [
        dict(section=1, semester=100, room=10, day="MON", start=time(9,0), end=time(11,0), instructors=[7])
    ]
    new = dict(section=2, semester=100, room=10, day="MON", start=time(10,0), end=time(12,0), instructors=[8])
    assert has_room_conflict(existing, new) is True

# TC-074: ทับซ้อนเพราะ “อาจารย์ซ้ำกัน”
def test_TC_074_instructor_conflict():
    existing = [
        dict(section=1, semester=100, room=10, day="MON", start=time(9,0), end=time(11,0), instructors=[7])
    ]
    new = dict(section=2, semester=100, room=11, day="MON", start=time(10,0), end=time(12,0), instructors=[7,9])
    assert has_instructor_conflict(existing, new) is True

# TC-075: เคสชนขอบ 11:00–12:00 ถือว่าทับ
def test_TC_075_touching_edges_conflict():
    existing = [
        dict(section=1, semester=100, room=10, day="MON", start=time(9,0), end=time(11,0), instructors=[7])
    ]
    new = dict(room=10, semester=100, day="MON", start=time(11,0), end=time(12,0), instructors=[8])
    assert overlaps(time(9,0), time(11,0), time(11,0), time(12,0), inclusive=True) is True
    assert has_room_conflict(existing, new) is True

# TC-076: คนละวันไม่ทับซ้อน
def test_TC_076_different_day_no_conflict():
    existing = [
        dict(section=1, semester=100, room=10, day="MON", start=time(9,0), end=time(11,0), instructors=[7])
    ]
    new = dict(day="TUE", start=time(9,30), end=time(10,30), room=10, semester=100, instructors=[7])
    assert not has_room_conflict(existing, new)
    assert not has_instructor_conflict(existing, new)

# TC-077: ห้อง/เวลาเดียวกันแต่คนละเทอมไม่ทับซ้อน
def test_TC_077_different_semester_no_conflict():
    existing = [
        dict(section=1, semester=100, room=10, day="MON", start=time(9,0), end=time(11,0), instructors=[7])
    ]
    new = dict(semester=101, room=10, day="MON", start=time(9,0), end=time(11,0), instructors=[8])
    assert not has_room_conflict(existing, new)
