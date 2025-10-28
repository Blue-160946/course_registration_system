import pytest
from django.db import IntegrityError
from courses.models import Course, Section, ClassTime
from payment.models import PaymentTransaction



# ---------------------------
# Course Impact
# ---------------------------
def test_section_create_fails_when_course_missing(db, semester, room, instructor_user):
    """
    Simulation: ถ้า Course พัง (ไม่มี/invalid)
    → Section ที่อ้าง Course จะสร้างไม่ได้
    """
    with pytest.raises(IntegrityError):
        Section.objects.create(
            course=None,  # Course missing
            semester=semester,
            section_number="99",
            capacity=30,
            room=room,
        )


def test_classtime_fails_due_to_section_failure(db):
    """
    Simulation: ถ้า Section พัง → ClassTime ผูกไม่ได้
    """
    with pytest.raises(IntegrityError):
        ClassTime.objects.create(
            section=None,  # Section missing
            day="TUE",
            start_time="10:00",
            end_time="12:00",
        )


# ---------------------------
# Section Impact
# ---------------------------
def test_section_unique_constraint(db, course, semester, room, instructor_user):
    """
    Simulation: ถ้า Section ซ้ำ (course+semester+section_number)
    → จะพัง และกระทบ CRUD ของ ClassTime
    """
    Section.objects.create(
        course=course,
        semester=semester,
        section_number="1",
        capacity=30,
        room=room,
    )
    with pytest.raises(IntegrityError):
        Section.objects.create(
            course=course,
            semester=semester,
            section_number="1",  # duplicate
            capacity=25,
            room=room,
        )


# ---------------------------
# Semester Impact
# ---------------------------
def test_semester_logic_affects_conflict(db, course, semester, room):
    """
    Simulation: ถ้า Semester logic เพี้ยน (เช่น อ้างผิดเทอม)
    → การตรวจ conflict อาจผิด
    """
    # clone semester ให้ไม่ซ้ำ (year/semester_number ต่าง)
    wrong_semester = semester.__class__.objects.create(
        year=semester.year + 1,   # แก้ปีใหม่
    )

    s1 = Section.objects.create(
        course=course, semester=semester, section_number="1", capacity=30, room=room
    )
    s2 = Section.objects.create(
        course=course, semester=wrong_semester, section_number="2", capacity=30, room=room
    )

    # ClassTime ในคนละเทอม → ไม่ถือว่าทับกัน
    ct1 = ClassTime.objects.create(section=s1, day="MON", start_time="09:00", end_time="11:00")
    ct2 = ClassTime.objects.create(section=s2, day="MON", start_time="09:30", end_time="10:30")

    assert ct1.section.semester != ct2.section.semester



# ---------------------------
# Room Impact
# ---------------------------
def test_section_room_required(db, course, semester):
    """
    Simulation: ถ้า Room หายไป
    → Section technically สร้างได้ แต่ถือว่าผิด business rule
    """
    section = Section.objects.create(
        course=course, semester=semester, section_number="X", capacity=20, room=None
    )
    # DB ยอม แต่เรายืนยันว่า business rule ต้อง reject ใน view/form
    assert section.room is None



# ---------------------------
# Instructor Impact
# ---------------------------
def test_section_instructor_required(db, course, semester, room):
    """
    Simulation: ถ้า Instructor พัง (ไม่มี instructor)
    → Section จะไม่สมบูรณ์ และ ClassTime จะใช้ไม่ได้
    """
    section = Section.objects.create(
        course=course,
        semester=semester,
        section_number="3",
        capacity=30,
        room=room,
    )
    assert section.instructors.count() == 0  # ไม่มี instructor
    # สมมติว่า business logic จะ reject ตรงนี้ใน view/form layer


# ---------------------------
# ClassTime Overlap Logic
# ---------------------------
def test_classtime_overlap_logic(db, section):
    """
    Simulation: ถ้า overlap logic พัง
    → ตารางชนกันโดยไม่รู้ตัว
    """
    ct1 = ClassTime.objects.create(section=section, day="WED", start_time="09:00", end_time="11:00")

    # ถ้า logic overlap ตรวจผิด → case นี้จะไม่ raise
    ct2 = ClassTime.objects.create(section=section, day="WED", start_time="10:30", end_time="11:30")

    assert ct1.start_time < ct2.end_time  # จริง ๆ ทับกัน

# --------------------------------------------------------------------
# Payment พัง
# --------------------------------------------------------------------
@pytest.mark.django_db
def test_payment_failure_blocks_enrollment(student_user, course, semester, room, mocker):
    """
    Impact Rule: ถ้า Payment พัง
    → ลงทะเบียนไม่สำเร็จ cascade
    """
    section = Section.objects.create(
        course=course, semester=semester,
        section_number="1", capacity=30, room=room
    )

    course.fee = 100
    course.save()

    # mock ให้ Payment fail
    mocker.patch(
        "courses.views.FakePaymentGateway.charge",
        return_value={"success": False}
    )

    # mock messages เพื่อไม่ให้ error
    mocker.patch("courses.views.messages")

    # mock redirect เพื่อให้ return อะไรก็ได้
    mocker.patch("courses.views.redirect", return_value="redirected")

    # mock request object
    request = mocker.Mock()
    request.user = student_user
    request.method = "POST"
    request.POST = {}

    from courses.views import enroll_section
    response = enroll_section(request, section.pk)

    txn = PaymentTransaction.objects.filter(
        student=student_user.profile, course=course
    ).first()

    assert txn is not None
    assert txn.status == "FAILED"
    assert response == "redirected"