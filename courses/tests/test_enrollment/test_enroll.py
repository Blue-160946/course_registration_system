import pytest
from django.urls import reverse
from courses.models import Section
from payment.models import PaymentTransaction
from courses.tests.test_enrollment.factories import SectionFactory, ProfileFactory, CourseFactory
from django.contrib.messages import get_messages

@pytest.mark.django_db
def test_enroll_free_course_success(client):
    # สร้างนิสิตและ Section
    student_profile = ProfileFactory(user_type='STUDENT')
    section = SectionFactory(capacity=30)

    # login ด้วย User ของ Profile
    client.force_login(student_profile.user)

    # เรียก view ลงทะเบียน
    url = reverse('courses:enroll-section', kwargs={'section_pk': section.pk})
    response = client.post(url)

    # ตรวจสอบ redirect
    assert response.status_code == 302

    # ตรวจสอบว่านิสิตถูกเพิ่ม
    section.refresh_from_db()
    assert student_profile.user in section.students.all()


@pytest.mark.django_db
def test_enroll_duplicate_section(client):
    # 
    student_profile = ProfileFactory(user_type='STUDENT')
    section = SectionFactory(capacity=30)
    section.students.add(student_profile.user)  # เพิ่มก่อนหน้าแล้ว

    client.force_login(student_profile.user)
    url = reverse('courses:enroll-section', kwargs={'section_pk': section.pk})
    response = client.post(url)

    # ควร redirect และไม่เพิ่มซ้ำ
    assert response.status_code == 302
    section.refresh_from_db()
    assert section.students.count() == 1
    assert student_profile.user in section.students.all()


# @pytest.mark.django_db
# def test_enroll_full_section(client):
#     student_profile = ProfileFactory(user_type='STUDENT')
#     section = SectionFactory(capacity=1)  # กำหนดให้เต็มทันที
#     another_student = ProfileFactory(user_type='STUDENT')
#     section.students.add(another_student.user)  # เติมเต็ม Section

#     client.force_login(student_profile.user)
#     url = reverse('courses:enroll-section', kwargs={'section_pk': section.pk})
#     response = client.post(url)

#     # ตรวจสอบ redirect และยังไม่เพิ่ม student ใหม่
#     assert response.status_code == 302
#     section.refresh_from_db()
#     assert student_profile not in section.students.all()
#     assert section.students.count() == 1

@pytest.mark.django_db
def test_enroll_paid_course_success(client):
    # สร้าง user และ login
    profile = ProfileFactory(user_type='STUDENT')
    user = profile.user
    client.force_login(user)

    # สร้าง course ที่มีค่าธรรมเนียม > 0
    course = CourseFactory(fee=500)
    section = SectionFactory(course=course)

    # patch fake payment ให้จ่ายผ่าน
    class FakeSuccessPayment:
        @staticmethod
        def charge(student, amount):
            return {"success": True, "transaction_id": "TX123"}

    from courses.views import FakePaymentGateway
    original_gateway = FakePaymentGateway
    try:
        # ใช้ FakeSuccessPayment แทน
        import courses.views
        courses.views.FakePaymentGateway = FakeSuccessPayment

        # เรียก enroll view
        url = reverse("courses:enroll-section", kwargs={"section_pk": section.pk})
        response = client.post(url, follow=True)

        # ตรวจสอบว่า redirect กลับ public section list
        assert response.status_code == 200

        # ตรวจสอบว่ามีการลงทะเบียนใน section
        section.refresh_from_db()
        assert user in section.students.all()

        # ตรวจสอบว่ามีการบันทึก transaction
        tx = PaymentTransaction.objects.get(student=profile, course=course)
        assert tx.amount == course.fee
        assert tx.status == "SUCCESS"

    finally:
        # คืนค่า original gateway
        courses.views.FakePaymentGateway = original_gateway

@pytest.mark.django_db
def test_enroll_paid_course_fail_payment(client):
    profile = ProfileFactory(user_type='STUDENT')
    user = profile.user
    client.force_login(user)

    course = CourseFactory(fee=500)
    section = SectionFactory(course=course)

    class FakeFailPayment:
        @staticmethod
        def charge(student, amount):
            return {"success": False}

    from courses.views import FakePaymentGateway
    original_gateway = FakePaymentGateway
    try:
        import courses.views
        courses.views.FakePaymentGateway = FakeFailPayment

        url = reverse("courses:enroll-section", kwargs={"section_pk": section.pk})
        response = client.post(url, follow=True)

        # ตรวจสอบ redirect
        assert response.status_code == 200
        assert response.request["PATH_INFO"] == reverse("courses:public-section-list")

        # ตรวจสอบ message error
        messages = list(get_messages(response.wsgi_request))
        assert any("การชำระเงินสำหรับวิชา" in str(m) for m in messages)

        # ตรวจสอบว่าไม่มีการลงทะเบียน
        assert user not in section.students.all()

        # ตรวจสอบว่ามี PaymentTransaction สถานะ FAILED
        tx = PaymentTransaction.objects.get(student=profile, course=course)
        assert tx.status == "FAILED"

    finally:
        courses.views.FakePaymentGateway = original_gateway