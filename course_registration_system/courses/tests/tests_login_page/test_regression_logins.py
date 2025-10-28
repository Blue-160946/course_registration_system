import pytest
from django.urls import reverse
import re
from django.contrib.messages import get_messages
from django.contrib.auth.forms import AuthenticationForm


@pytest.mark.regression_unit_test
@pytest.mark.django_db
def test_TC_001_user_staff_can_login_with_correct(new_staff, data_regression):
    """
    ทดสอบการล็อกอินของ staff ด้วยข้อมูลที่ถูกต้อง
    - ใช้ new_user_staff fixture ในการสร้างผู้ใช้
    - ล็อกอิน username และ password ที่ถูกต้อง
    - form ต้อง valid
    """

    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_data = {
        'username': new_staff.username,
        'password': '123456789'
    }
    
    # ตรวจสอบว่าฟอร์ม valid ก่อน
    form = AuthenticationForm(data=login_data)
    assert form.is_valid(), f"Form errors: {form.errors}"
    
    
    # เก็บข้อมูล snapshot สำหรับ regression test
    snapshot_data = {
        'form_valid': form.is_valid(),
        "form_errors": form.errors.get_json_data() if form.errors else {},
    }

    # ใช้ data_regression เก็บ snapshot
    data_regression.check(snapshot_data)
    

@pytest.mark.regression_unit_test
@pytest.mark.django_db
def test_TC_002_user_staff_login_without_username(new_staff, data_regression):
    """
    Regression Test:
    - ใช้ new_user_staff fixture ในการสร้างผู้ใช้
    - ล็อกอินโดยไม่กรอก username
    - form ต้องไม่ valid
    """

    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_data = {
        'username': "",
        'password': '123456789'
    }

    # ตรวจสอบว่าฟอร์ม valid ก่อน
    form = AuthenticationForm(data=login_data)
    assert not form.is_valid()  # form ต้องไม่ valid
    
    # เก็บข้อมูล snapshot สำหรับ regression test
    snapshot_data = {
        "form_valid": form.is_valid(),
        "form_errors": {field: list(errors) for field, errors in form.errors.items()},
    }
    
    # ใช้ data_regression เก็บ snapshot
    data_regression.check(snapshot_data)
    
    
@pytest.mark.regression_unit_test
@pytest.mark.django_db
def test_TC_003_user_staff_login_without_password(new_staff, data_regression):
    """
    Regression Test:
    - ล็อกอินโดยไม่กรอก password
    - form ต้องไม่ valid
    """
    
    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_data = {
        'username': new_staff.username,
        'password': ''
    }

    # ตรวจสอบว่าฟอร์ม valid ก่อน
    form = AuthenticationForm(data=login_data)
    assert not form.is_valid()  # form ต้องไม่ valid
    
    # เก็บข้อมูล snapshot สำหรับ regression test
    snapshot_data = {
        "form_valid": form.is_valid(),
        "form_errors": {field: list(errors) for field, errors in form.errors.items()},
    }
    
    # ใช้ data_regression เก็บ snapshot
    data_regression.check(snapshot_data)
    
    
@pytest.mark.regression_unit_test
@pytest.mark.django_db
def test_TC_004_user_staff_login_without_username_and_password(new_staff, data_regression):
    """
    Regression Test:
    - ล็อกอินโดยไม่กรอก username และ password
    - เก็บ snapshot
    """

    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_data = {
        'username': '',
        'password': ''
    }

    # ตรวจสอบว่าฟอร์ม valid
    form = AuthenticationForm(data=login_data)
    assert not form.is_valid()  # form ต้องไม่ valid
    
    # เก็บข้อมูล snapshot สำหรับ regression test
    snapshot_data = {
        "form_valid": form.is_valid(),
        "form_errors": {field: list(errors) for field, errors in form.errors.items()},
    }
    
    # ใช้ data_regression เก็บ snapshot
    data_regression.check(snapshot_data)
    
    
@pytest.mark.regression_unit_test
@pytest.mark.django_db
def test_TC_005_user_staff_login_with_incorrect_username(new_staff, data_regression):
    """
    Regression Test:
    - ล็อกอินโดยใช้ username ที่ไม่ถูกต้อง
    - เก็บ snapshot
    """

    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_data = {
        'username': 'wrong_username',
        'password': '123456789'
    }

    # ตรวจสอบการ response
    form = AuthenticationForm(data=login_data)
    assert not form.is_valid()  # form ต้องไม่ valid
    

    # เก็บข้อมูล snapshot สำหรับ regression test
    snapshot_data = {
        "form_valid": form.is_valid(),
        "form_errors": {field: list(errors) for field, errors in form.errors.items()},
    }

    # ใช้ data_regression เก็บ snapshot
    data_regression.check(snapshot_data)
    

@pytest.mark.regression_unit_test
@pytest.mark.django_db
def test_TC_006_user_staff_login_with_incorrect_password(new_staff, data_regression):
    """
    Regression Test:
    - ล็อกอินโดยใช้ password ที่ไม่ถูกต้อง
    - เก็บ snapshot เฉพาะข้อความ error ของฟอร์ม
    """

    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_data = {
        'username': new_staff.username,
        'password': 'wrong_password'
    }

    # ตรวจสอบการ response
    form = AuthenticationForm(data=login_data)
    assert not form.is_valid()  # form ต้องไม่ valid
    

    # เก็บข้อมูล snapshot สำหรับ regression test
    snapshot_data = {
        "form_valid": form.is_valid(),
        "form_errors": {field: list(errors) for field, errors in form.errors.items()},
    }

    # ใช้ data_regression เก็บ snapshot
    data_regression.check(snapshot_data)
    
    
@pytest.mark.regression_unit_test
@pytest.mark.django_db
def test_TC_007_user_staff_login_with_space_in_username_and_password(new_staff, data_regression):
    """
    Regression Test:
    - ล็อกอินโดยใช้ username และ password ที่ค่าเป็นช่องว่าง
    - เก็บ snapshot เฉพาะข้อความ error ของฟอร์ม
    """

    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_data = {
        'username': ' ',
        'password': ' '
    }


    # ตรวจสอบการ response
    form = AuthenticationForm(data=login_data)
    assert not form.is_valid()  # form ต้องไม่ valid


    # เก็บข้อมูล snapshot สำหรับ regression test
    snapshot_data = {
        "form_valid": form.is_valid(),
        "form_errors": {field: list(errors) for field, errors in form.errors.items()},
    }


    # ใช้ data_regression เก็บ snapshot
    data_regression.check(snapshot_data)
    
    
@pytest.mark.regression_unit_test
@pytest.mark.django_db
def test_TC_008_login_page_has_csrf_token(client, data_regression):
    """
    ทดสอบว่าในหน้า login มี CSRF token ใน form
    """

    login_url = reverse('users:login')

    # GET หน้า login
    response = client.get(login_url)
    html = response.content.decode()
    assert response.status_code == 200
    
    # ตรวจสอบว่าใน HTML มี <form>
    assert "<form" in html, "หน้า login ต้องมี <form>"

    # ตรวจสอบว่า context มี csrf_token
    has_csrf = 'csrfmiddlewaretoken' in html
    assert has_csrf, "ฟอร์มต้องมี input csrfmiddlewaretoken"

    # snapshot ข้อมูลสำหรับ regression
    snapshot_data = {
        "status_code": response.status_code,
        "has_form": "<form" in html,
        "has_csrf_token": has_csrf,
    }
    data_regression.check(snapshot_data)

    

@pytest.mark.regression_integration_test
@pytest.mark.django_db
def test_TC_009_user_login_and_access_protected_page_regression(
    client, new_staff, data_regression, file_regression
):
    """
    Regression Test: ทดสอบการล็อกอินและการเข้าถึงหน้าที่ต้องล็อกอิน
    ตรวจสอบว่า behavior ไม่เปลี่ยนจาก baseline
    """
    login_url = reverse('users:login')
    course_list_url = reverse('courses:course-list')

    # 1. ก่อนล็อกอิน
    response = client.get(course_list_url)

    # 2. ล็อกอิน
    login_response = client.post(login_url, {
        'username': new_staff.username,
        'password': '123456789'
    })
    
    # 3. เก็บข้อมูล snapshot สำหรับ regression test
    data_regression.check({
    "before_login": {
        "status_code": response.status_code,
        "redirect_url": response.url,
    },
    "after_login": {
        "status_code": login_response.status_code,
        "redirect_url": login_response.url,
        "is_authenticated": login_response.wsgi_request.user.is_authenticated,
        "is_staff": login_response.wsgi_request.user.is_staff,
    },
    })

    # 4. เก็บข้อมูล snapshot HTML ของหน้าหลังล็อกอิน สำหรับ regression test
    # เก็บ HTML snapshot หลังล็อกอิน
    response = client.get(course_list_url)
    html = response.content.decode("utf-8")

    # ลบ CSRF token ออก (แทนด้วย placeholder)
    html = re.sub(
        r'name="csrfmiddlewaretoken" value="[^"]+"',
        'name="csrfmiddlewaretoken" value="CSRF_TOKEN"',
        html
    )

    file_regression.check(
        html,
        extension=".html",
        encoding="utf-8"
    )
    
    
@pytest.mark.regression_integration_test
@pytest.mark.django_db
def test_TC_010_user_login_with_incorrect_password(
    client, new_staff, data_regression, file_regression
):
    """
    Regression Test: ทดสอบการล็อกอินด้วยรหัสผ่านผิด และตรวจสอบข้อความ error
    ตรวจสอบว่า behavior ไม่เปลี่ยนจาก baseline
    """
    login_url = reverse('users:login')

    # 1. ล็อกอินด้วยรหัสผ่านผิด
    login_response = client.post(login_url, {
        'username': new_staff.username,
        'password': 'wrongpassword'
    })
    
    # ดึงข้อความ error จาก messages framework
    messages = [str(m) for m in get_messages(login_response.wsgi_request)]

    # 2. เก็บข้อมูล snapshot สำหรับ regression test
    data_regression.check({
        "after_login": {
            "status_code": login_response.status_code,
            "is_authenticated": login_response.wsgi_request.user.is_authenticated,
            "is_staff": login_response.wsgi_request.user.is_staff,
            "messages": messages,
        },
    })

    # 3. เก็บข้อมูล snapshot HTML ของหน้าหลังล็อกอิน สำหรับ regression test
    html = login_response.content.decode("utf-8")

    # ลบ CSRF token ออก (แทนด้วย placeholder)
    html = re.sub(
        r'name="csrfmiddlewaretoken" value="[^"]+"',
        'name="csrfmiddlewaretoken" value="CSRF_TOKEN"',
        html
    )

    file_regression.check(
        html,
        extension=".html",
        encoding="utf-8"
    )
    
    
@pytest.mark.regression_integration_test
@pytest.mark.django_db
def test_TC_011_login_fails_with_non_user_in_system(
    client, data_regression, file_regression
):
    """
    Regression Test: ทดสอบการล็อกอินด้วยผู้ใช้ที่ไม่มีในระบบ
    ตรวจสอบว่า behavior ไม่เปลี่ยนจาก baseline
    """
    login_url = reverse('users:login')

    # 1. ล็อกอินด้วยผู้ใช้ที่ไม่มีในระบบ
    login_response = client.post(login_url, {
        'username': 'wrong_username',
        'password': '123456789'
    })
    
    # ดึงข้อความ error จาก messages framework
    messages = [str(m) for m in get_messages(login_response.wsgi_request)]

    # 2. เก็บข้อมูล snapshot สำหรับ regression test
    data_regression.check({
        "after_login": {
            "status_code": login_response.status_code,
            "is_authenticated": login_response.wsgi_request.user.is_authenticated,
            "is_staff": login_response.wsgi_request.user.is_staff,
            "messages": messages,
        },
    })

    # 3. เก็บข้อมูล snapshot HTML ของหน้าหลังล็อกอิน สำหรับ regression test
    html = login_response.content.decode("utf-8")

    # ลบ CSRF token ออก (แทนด้วย placeholder)
    html = re.sub(
        r'name="csrfmiddlewaretoken" value="[^"]+"',
        'name="csrfmiddlewaretoken" value="CSRF_TOKEN"',
        html
    )

    file_regression.check(
        html,
        extension=".html",
        encoding="utf-8"
    )
    

@pytest.mark.regression_integration_test
@pytest.mark.django_db
def test_TC_012_user_login_with_space_in_username_and_password(
    client, data_regression, file_regression
):
    """
    Regression Test: ทดสอบการล็อกอินด้วย username และ password ที่มีช่องว่าง
    ตรวจสอบว่า behavior ไม่เปลี่ยนจาก baseline
    """
    login_url = reverse('users:login')

    # 1. ล็อกอินด้วย username และ password ที่มีช่องว่างนำหน้า/ตามหลัง
    login_response = client.post(login_url, {
        'username': ' ',
        'password': ' '
    })
    
    # ดึงข้อความ error จาก messages framework
    messages = [str(m) for m in get_messages(login_response.wsgi_request)]

    # 2. เก็บข้อมูล snapshot สำหรับ regression test
    data_regression.check({
        "after_login": {
            "status_code": login_response.status_code,
            "is_authenticated": login_response.wsgi_request.user.is_authenticated,
            "is_staff": login_response.wsgi_request.user.is_staff,
            "messages": messages,
        },
    })

    # 3. เก็บข้อมูล snapshot HTML ของหน้าหลังล็อกอิน สำหรับ regression test
    html = login_response.content.decode("utf-8")

    # ลบ CSRF token ออก (แทนด้วย placeholder)
    html = re.sub(
        r'name="csrfmiddlewaretoken" value="[^"]+"',
        'name="csrfmiddlewaretoken" value="CSRF_TOKEN"',
        html
    )

    file_regression.check(
        html,
        extension=".html",
        encoding="utf-8"
    )
    

@pytest.mark.regression_integration_test
@pytest.mark.django_db
def test_TC_013_login_with_disabled_user(
    client, new_staff, data_regression, file_regression
):
    """
    Regression Test: ทดสอบการล็อกอินด้วยผู้ใช้ที่ถูกปิดใช้งาน (is_active=False)
    ตรวจสอบว่า behavior ไม่เปลี่ยนจาก baseline
    """
    login_url = reverse('users:login')

    # ปิดใช้งานผู้ใช้
    new_staff.is_active = False
    new_staff.save()

    # 1. ล็อกอินด้วยผู้ใช้ที่ถูกปิดใช้งาน
    login_response = client.post(login_url, {
        'username': new_staff.username,
        'password': '123456789'
    })

    # 2. เก็บข้อมูล snapshot สำหรับ regression test
    data_regression.check({
        "after_login": {
            "status_code": login_response.status_code,
            "is_authenticated": login_response.wsgi_request.user.is_authenticated,
            "is_staff": login_response.wsgi_request.user.is_staff,
        },
    })

    # 3. เก็บข้อมูล snapshot HTML ของหน้าหลังล็อกอิน สำหรับ regression test
    html = login_response.content.decode("utf-8")

    # ลบ CSRF token ออก (แทนด้วย placeholder)
    html = re.sub(
        r'name="csrfmiddlewaretoken" value="[^"]+"',
        'name="csrfmiddlewaretoken" value="CSRF_TOKEN"',
        html
    )

    file_regression.check(
        html,
        extension=".html",
        encoding="utf-8"
    )
    
    
@pytest.mark.regression_integration_test
@pytest.mark.django_db
def test_TC_014_user_login_without_csrf_token(
    client, new_staff, data_regression, file_regression
):
    """
    Regression Test: ทดสอบการล็อกอินโดยไม่ส่ง CSRF token
    ตรวจสอบว่า behavior ไม่เปลี่ยนจาก baseline
    """
    
    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')
    
    # เปิดการตรวจสอบ CSRF ใน client ชั่วคราว
    client.handler.enforce_csrf_checks = True

    # ล็อกอินโดยไม่ส่ง CSRF token
    login_response = client.post(login_url, {
        'username': new_staff.username,
        'password': '123456789'
    })
    
    data_regression.check({
        "status_code": login_response.status_code,
        "reason_phrase": login_response.reason_phrase,
    })
    
    # เก็บข้อมูล snapshot HTML ของหน้าหลังล็อกอิน สำหรับ regression test
    html = login_response.content.decode("utf-8")

    file_regression.check(
        html,
        extension=".html",
        encoding="utf-8"
    )
    
    