import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from tests import factories
from users.models import Profile

@pytest.mark.integration
@pytest.mark.django_db
def test_staff_login_view_redirects_authenticated_user(client, admin_user):
    # Arrange: ล็อกอินไว้ก่อนเรียก view
    client.force_login(admin_user)

    # Act: เปิดหน้า login
    response = client.get(reverse("users:login"))

    # Assert: ควร redirect ไปหน้า index
    assert response.status_code == 302
    assert response.headers["Location"] == reverse("core:index")

@pytest.mark.integration
@pytest.mark.django_db
def test_staff_login_view_allows_staff_login(client):
    # Arrange: สร้าง staff user ที่มีรหัสผ่านที่รู้ค่า
    staff_user = factories.UserFactory(is_staff=True)

    # Act: ส่ง POST ด้วยข้อมูลที่ถูกต้อง
    response = client.post(
        reverse("users:login"),
        data={"username": staff_user.username, "password": "TestPass123!"},
    )

    # Assert: ต้อง redirect ไปหน้ารายวิชา staff
    assert response.status_code == 302
    assert response.headers["Location"] == reverse("courses:course-list")

@pytest.mark.integration
@pytest.mark.django_db
def test_staff_login_view_redirects_student_to_public_section(client):
    # Arrange: มีนักศึกษาที่รู้รหัสผ่าน
    student = factories.StudentFactory()

    # Act: ล็อกอินด้วยข้อมูลนักศึกษา
    response = client.post(
        reverse("users:login"),
        data={"username": student.user.username, "password": "TestPass123!"},
    )

    # Assert: ต้องส่งไปยังหน้าลงทะเบียนสาธารณะ
    assert response.status_code == 302
    assert response.headers["Location"] == reverse("courses:public-section-list")

@pytest.mark.integration
@pytest.mark.django_db
def test_staff_login_view_rejects_non_staff_non_student(client):
    # Arrange: ผู้ใช้ที่มี profile ประเภทอาจารย์
    instructor_user = factories.UserFactory()
    Profile.objects.create(
        user=instructor_user,
        user_type=Profile.UserType.INSTRUCTOR,
        department=factories.DepartmentFactory(),
        acdemic_title=Profile.AcademicTitle.LECTURER,
    )

    # Act: ส่ง POST แล้วควรโดน error message
    response = client.post(
        reverse("users:login"),
        data={"username": instructor_user.username, "password": "TestPass123!"},
        follow=True,
    )

    # Assert: ต้องอยู่หน้าเดิมและขึ้นข้อความ error
    assert response.redirect_chain[-1][0].endswith(reverse("users:login"))
    messages = list(get_messages(response.wsgi_request))
    assert any("สิทธิ์" in message.message for message in messages)
