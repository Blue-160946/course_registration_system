import pytest
from django.contrib import admin
from django.test import override_settings

from tests import factories
from users.models import Profile

# ลงทะเบียน ProfileAdmin ชั่วคราวเพื่อให้มี URL ในระบบ admin
if Profile not in admin.site._registry:
    admin.site.register(Profile)


def _admin_post(client, url, data):
    response = client.post(url, data, follow=False)
    if hasattr(response, "render") and callable(response.render):
        response.render()
    return response


@pytest.mark.integration
@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=["testserver"])
def test_admin_add_student_requires_branch(client):
    # Arrange: ล็อกอินเป็น admin และเตรียม user นักศึกษาที่ไม่เลือกสาขา
    admin_user = factories.UserFactory(is_staff=True, is_superuser=True)
    target_user = factories.UserFactory(username="student-missing-admin")
    client.force_login(admin_user)
    add_url = "/admin/users/profile/add/"
    payload = {
        "user": str(target_user.pk),
        "user_type": Profile.UserType.STUDENT,
        "name_title": "",
        "first_name_th": "",
        "last_name_th": "",
        "gender": "",
        "date_of_birth": "",
        "phone_number": "",
        "address": "",
        "student_id": "77000000",
        "branch": "",
        "student_status": Profile.StudentStatus.STUDYING,
        "acdemic_title": "",
        "department": "",
        "job_title": "",
        "_save": "Save",
    }

    # Act: ส่งฟอร์มที่ไม่เลือก branch ให้ admin
    response = _admin_post(client, add_url, payload)

    # Assert: ฟอร์มต้องบอกให้เลือก branch และไม่สร้าง Profile
    assert response.status_code == 200
    form = response.context_data["adminform"].form
    assert "branch" in form.errors
    assert not Profile.objects.filter(user=target_user).exists()


@pytest.mark.integration
@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=["testserver"])
def test_admin_add_instructor_requires_academic_title(client):
    # Arrange: ล็อกอิน admin และเตรียม user อาจารย์ที่ไม่ระบุ acdemic_title
    admin_user = factories.UserFactory(is_staff=True, is_superuser=True)
    instructor_user = factories.UserFactory(username="instructor-missing-admin")
    client.force_login(admin_user)
    add_url = "/admin/users/profile/add/"
    department = factories.DepartmentFactory()
    payload = {
        "user": str(instructor_user.pk),
        "user_type": Profile.UserType.INSTRUCTOR,
        "name_title": "",
        "first_name_th": "",
        "last_name_th": "",
        "gender": "",
        "date_of_birth": "",
        "phone_number": "",
        "address": "",
        "student_id": "",
        "branch": "",
        "student_status": "",
        "acdemic_title": "",
        "department": str(department.pk),
        "job_title": "",
        "_save": "Save",
    }

    # Act: บันทึกข้อมูลอาจารย์ที่ขาดตำแหน่งทางวิชาการ
    response = _admin_post(client, add_url, payload)

    # Assert: ฟอร์มต้องแจ้งให้กรอก acdemic_title และไม่สร้าง Profile
    assert response.status_code == 200
    form = response.context_data["adminform"].form
    assert "acdemic_title" in form.errors
    assert not Profile.objects.filter(user=instructor_user).exists()
