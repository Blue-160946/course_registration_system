import pytest
from django.urls import reverse
from django.contrib.messages import get_messages


@pytest.mark.unit_test
@pytest.mark.django_db
def test_TC_001_user_staff_can_login_with_correct(client, new_staff):
    """
    ทดสอบการล็อกอินของ staff ด้วยข้อมูลที่ถูกต้อง
    - ใช้ new_user_staff fixture ในการสร้างผู้ใช้
    - ใช้ username และ password ที่ถูกต้อง
    - ต้องล็อกอินสำเร็จ
    - ต้อง redirect ไปที่หน้า course-list
    """

    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')
    
    # ทดสอบการล็อกอิน
    response = client.post(login_url, {
        'username': new_staff.username,
        'password': '123456789'
    })
    
    # ตรวจสอบผลลัพธ์
    assert response.status_code == 302  # ต้องมีการ redirect
    
    
@pytest.mark.unit_test
@pytest.mark.django_db
def test_TC_002_user_staff_login_without_username(client, new_staff):
    """
    ทดสอบการล็อกอินของ staff โดยไม่กรอก username
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    - ต้องแสดง validation message ในฟอร์ม
    - ต้องแสดง error message
    - ต้องไม่สามารถเข้าถึงหน้าที่ต้องล็อกอิน
    """
    
    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')
    
    # ทดสอบการเข้าถึงหน้า login
    get_response = client.get(login_url)
    assert get_response.status_code == 200
    assert 'form' in get_response.context
    
    # ทดสอบการล็อกอินโดยไม่กรอก username
    response = client.post(login_url, {
        'username': '',
        'password': '123456789'
    })
    
    # ตรวจสอบการ response
    assert response.status_code == 200  # ต้องอยู่ที่หน้า login
    
    # ตรวจสอบ form
    assert 'form' in response.context  # ต้องมี form กลับมา
    form = response.context['form']
    assert not form.is_valid()  # form ต้องไม่ valid
    
    # ตรวจสอบ validation message ในฟอร์ม
    content = response.content.decode('utf-8')
    assert "กรุณากรอกชื่อผู้ใช้" in content  # ข้อความ error จาก template
    

@pytest.mark.unit_test
@pytest.mark.django_db
def test_TC_003_user_staff_login_without_password(client, new_staff):
    """
    ทดสอบการล็อกอินของ staff โดยไม่กรอก password
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    """
    
    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')
    
    # ทดสอบการล็อกอินโดยไม่กรอก password
    response = client.post(login_url, {
        'username': new_staff.username,
        'password': ''
    })
    
    # ตรวจสอบผลลัพธ์
    assert response.status_code == 200
    
    # ตรวจสอบ form
    assert 'form' in response.context  # ต้องมี form กลับมา
    form = response.context['form']
    assert not form.is_valid()  # form ต้องไม่ valid
    
    # ตรวจสอบ validation message ในฟอร์ม
    content = response.content.decode('utf-8')
    assert "กรุณากรอกรหัสผ่าน" in content  # ข้อความ error จาก template
    
@pytest.mark.unit_test
@pytest.mark.django_db
def test_TC_004_user_staff_login_without_username_and_password(client):
    """
    ทดสอบการล็อกอินของ staff โดยไม่กรอก username และ password
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    """
    
    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')
    
    # ทดสอบการล็อกอินโดยไม่กรอกข้อมูลใดๆ
    response = client.post(login_url, {
        'username': '',
        'password': ''
    })
    
    # ตรวจสอบผลลัพธ์
    assert response.status_code == 200
    
    # ตรวจสอบ form
    assert 'form' in response.context  # ต้องมี form กลับมา
    form = response.context['form']
    assert not form.is_valid()  # form ต้องไม่ valid
    
    # ตรวจสอบ validation message ในฟอร์ม
    content = response.content.decode('utf-8')
    assert "กรุณากรอกชื่อผู้ใช้" in content  # ข้อความ error จาก template
    assert "กรุณากรอกรหัสผ่าน" in content  # ข้อความ error จาก template
    
    
@pytest.mark.unit_test
@pytest.mark.django_db
def test_TC_005_user_staff_login_with_incorrect_username(client, new_staff):
    """
    ทดสอบการล็อกอินของ staff ด้วย username ที่ไม่ถูกต้อง
    - ใช้ username ที่ไม่ถูกต้อง
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    """
    
    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')
    
    # ทดสอบการล็อกอินด้วย username ที่ไม่ถูกต้อง
    response = client.post(login_url, {
        'username': 'wrong_username',
        'password': '123456789'
    })
    
    # ตรวจสอบผลลัพธ์
    assert response.status_code == 200
    
    # ตรวจสอบ error messages จาก Django Messages Framework
    messages = list(response.context.get('messages', []))
    assert len(messages) > 0  # ต้องมี message อย่างน้อย 1 ข้อความ
    assert 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง' in str(messages[0])
    

@pytest.mark.unit_test
@pytest.mark.django_db
def test_TC_006_user_staff_login_with_incorrect_password(client, new_staff):
    """
    ทดสอบการล็อกอินของ staff ด้วย password ที่ไม่ถูกต้อง
    - ใช้ password ที่ไม่ถูกต้อง
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    """
    
    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')
    
    # ทดสอบการล็อกอินด้วย password ที่ไม่ถูกต้อง
    response = client.post(login_url, {
        'username': new_staff.username,
        'password': 'wrong_password'
    })
    
    # ตรวจสอบผลลัพธ์
    assert response.status_code == 200
    
    # ตรวจสอบ error messages จาก Django Messages Framework
    messages = list(response.context.get('messages', []))
    assert len(messages) > 0  # ต้องมี message อย่างน้อย 1 ข้อความ
    assert 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง' in str(messages[0])


@pytest.mark.unit_test
@pytest.mark.django_db
def test_TC_007_user_staff_login_with_space_in_username_and_password(client):
    """
    ทดสอบการล็อกอินของ staff โดยมี space ใน username และ password
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    """
    
    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')
    
    # ทดสอบการล็อกอินโดยมี space ใน username และ password
    response = client.post(login_url, {
        'username': ' ',
        'password': ' '
    })
    
    # ตรวจสอบผลลัพธ์
    assert response.status_code == 200
    
    # ตรวจสอบ error messages จาก Django Messages Framework
    messages = list(response.context.get('messages', []))
    assert len(messages) > 0  # ต้องมี message อย่างน้อย 1 ข้อความ
    assert 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง' in str(messages[0])
    

@pytest.mark.unit_test
@pytest.mark.django_db
def test_TC_008_check_login_page_csrf_token(client, new_staff):
    """
    ทดสอบการป้องกัน CSRF ในหน้า login
    - ต้องมี CSRF token ในหน้า login
    - ต้องไม่สามารถ login ได้ถ้าไม่มี CSRF token
    - ต้องมี error message เมื่อไม่มี CSRF token
    """
    
    # เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')
    
    # ทดสอบเข้าหน้า login ต้องมี CSRF token
    response = client.get(login_url)
    assert response.status_code == 200
    assert 'csrfmiddlewaretoken' in response.content.decode()
    
    # ทดสอบ login โดยไม่มี CSRF token
    # ปิดการตรวจสอบ CSRF ใน client ชั่วคราว
    client.handler.enforce_csrf_checks = True
    
    # ทำการ login โดยไม่มี CSRF token
    response = client.post(login_url, {
        'username': new_staff.username,
        'password': '123456789'
    })
    
    # ตรวจสอบว่าต้องไม่สามารถ login ได้
    assert response.status_code == 403  # CSRF verification failed
    

@pytest.mark.integration_test
@pytest.mark.django_db
def test_TC_009_user_login_and_access_protected_page(client, new_staff):
    """
    Integration test: ทดสอบการล็อกอินและการเข้าถึงหน้าที่ต้องล็อกอิน
    ทดสอบการทำงานร่วมกันของ:
    1. ระบบล็อกอิน
    2. ระบบการจัดการสิทธิ์
    3. การ redirect ไปยังหน้าที่ต้องการ
    4. การรักษาสถานะการล็อกอิน
    5. การป้องกันการเข้าถึงหน้าที่ต้องล็อกอิน
    """
    # 1. เตรียมข้อมูล URLs
    login_url = reverse('users:login')
    course_list_url = reverse('courses:course-list')
    
    # 2. ทดสอบการเข้าถึงหน้าที่ต้องล็อกอินก่อนล็อกอิน
    response = client.get(course_list_url)
    assert response.status_code == 302  # ต้องถูก redirect
    assert '/users/login/' in response.url  # ต้อง redirect ไปหน้า login
        
    # 3. ทดสอบการล็อกอิน
    login_response = client.post(login_url, {
        'username': 'admin',
        'password': '123456789'
    })
    assert login_response.status_code == 302  # ต้องมีการ redirect
    assert course_list_url in login_response.url  # redirect ไปที่ course-list
    
    # 4. ตรวจสอบว่า session ถูกสร้างขึ้น
    assert '_auth_user_id' in client.session
    assert int(client.session['_auth_user_id']) == new_staff.pk
    
    # 5. ตรวจสอบสถานะการล็อกอิน
    assert login_response.wsgi_request.user.is_authenticated
    assert login_response.wsgi_request.user.is_staff
    
    # 6. ทดสอบการเข้าถึงหน้าต่างๆ หลังล็อกอิน
    response = client.get(course_list_url)
    assert response.status_code == 200  # ต้องเข้าถึงได้
    assert response.wsgi_request.user.is_authenticated  # ต้องยังล็อกอินอยู่
    

@pytest.mark.integration_test
@pytest.mark.django_db
def test_TC_010_user_login_with_incorrect_password(client, new_staff):
    """
    Integration test: ทดสอบการล็อกอินด้วยรหัสผ่านที่ไม่ถูกต้อง
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    - ต้องไม่สามารถเข้าถึงหน้าที่ต้องล็อกอินได้
    """
    # 1. Arrange: เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')

    # 2. Act: ส่งคำขอ POST เพื่อล็อกอินด้วยรหัสผ่านที่ผิด
    login_response = client.post(login_url, {
        'username': new_staff.username,  # ใช้ username จาก fixture
        'password': 'wrong_password' # รหัสผ่านที่ผิด
    })

    # 3. Assert (การตรวจสอบเมื่อล็อกอินล้มเหลว)
    # 3.1 ตรวจสอบว่าระบบยังอยู่ที่หน้าเดิม (status_code 200)
    assert login_response.status_code == 200
    
    # 3.2 ตรวจสอบข้อความผิดพลาดใน Django Messages Framework
    messages = list(get_messages(login_response.wsgi_request))
    expected_message = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
    assert str(messages[0]) == expected_message
    
    # 3.3 ตรวจสอบว่าไม่มี session ถูกสร้างขึ้น
    assert '_auth_user_id' not in client.session
    


@pytest.mark.integration_test
@pytest.mark.django_db
def test_TC_011_login_fails_with_non_user_in_system(client):
    """
    Integration test: ทดสอบการล็อกอินด้วยผู้ใช้ที่ไม่มีในระบบ
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    - ต้องไม่สามารถเข้าถึงหน้าที่ต้องล็อกอินได้
    """
    
    # 1. Arrange: เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')

    # 2. Act: ส่งคำขอ POST เพื่อล็อกอินด้วยผู้ใช้ที่ไม่มีในระบบ
    login_response = client.post(login_url, {
        'username': 'wrong_username',
        'password': '123456789'
    })

    # 3. Assert (การตรวจสอบเมื่อล็อกอินล้มเหลว)
    # 3.1 ตรวจสอบว่าระบบยังอยู่ที่หน้าเดิม (status_code 200)
    assert login_response.status_code == 200
    
    # 3.2 ตรวจสอบข้อความผิดพลาดใน Django Messages Framework
    messages = list(get_messages(login_response.wsgi_request))
    expected_message = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
    assert str(messages[0]) == expected_message
    
    # 3.3 ตรวจสอบว่าไม่มี session ถูกสร้างขึ้น
    assert '_auth_user_id' not in client.session
    

@pytest.mark.integration_test
@pytest.mark.django_db
def test_TC_012_user_login_with_space_in_username_and_password(client):
    """
    Integration test: ทดสอบการล็อกอินโดยมี space ใน username และ password
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    - ต้องไม่สามารถเข้าถึงหน้าที่ต้องล็อกอินได้
    """
    
    # 1. Arrange: เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')

    # 2. Act: ส่งคำขอ POST เพื่อล็อกอินโดยมี space ใน username และ password
    login_response = client.post(login_url, {
        'username': ' ',
        'password': ' '
    })

    # 3. Assert (การตรวจสอบเมื่อล็อกอินล้มเหลว)
    # 3.1 ตรวจสอบว่าระบบยังอยู่ที่หน้าเดิม (status_code 200)
    assert login_response.status_code == 200
    
    # 3.2 ตรวจสอบข้อความผิดพลาดใน Django Messages Framework
    messages = list(get_messages(login_response.wsgi_request))
    expected_message = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
    assert str(messages[0]) == expected_message
    
    # 3.3 ตรวจสอบว่าไม่มี session ถูกสร้างขึ้น
    assert '_auth_user_id' not in client.session
    

@pytest.mark.integration_test
@pytest.mark.django_db
def test_TC_013_login_with_disabled_user(client, new_staff):
    """
    Integration test: ทดสอบการล็อกอินด้วยผู้ใช้ที่ถูกปิดใช้งาน (is_active=False)
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องกลับไปที่หน้า login พร้อมแสดงข้อความ error
    - ต้องไม่สามารถเข้าถึงหน้าที่ต้องล็อกอินได้
    """
    # ปิดการใช้งานผู้ใช้
    new_staff.is_active = False
    new_staff.save()
    
    # 1. Arrange: เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')

    # 2. Act: ส่งคำขอ POST เพื่อล็อกอินด้วยผู้ใช้ที่ถูกปิดใช้งาน
    login_response = client.post(login_url, {
        'username': new_staff.username,
        'password': '123456789'
    })

    # 3. Assert (การตรวจสอบเมื่อล็อกอินล้มเหลว)
    # 3.1 ตรวจสอบว่าระบบยังอยู่ที่หน้าเดิม (status_code 200)
    assert login_response.status_code == 200
    
    # 3.2 ตรวจสอบข้อความผิดพลาดใน Django Messages Framework
    messages = list(get_messages(login_response.wsgi_request))
    expected_message = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
    assert str(messages[0]) == expected_message
    
    # 3.3 ตรวจสอบว่าไม่มี session ถูกสร้างขึ้น
    assert '_auth_user_id' not in client.session
    
    
@pytest.mark.integration_test
@pytest.mark.django_db
def test_TC_014_user_login_without_csrf_token(client, new_staff):
    """
    Integration test: ทดสอบการล็อกอินโดยไม่มี CSRF token
    - ต้องล็อกอินไม่สำเร็จ
    - ต้องได้รับ HTTP 403 Forbidden
    - ต้องไม่สามารถเข้าถึงหน้าที่ต้องล็อกอินได้
    """
    # เปิดการตรวจสอบ CSRF ใน client ชั่วคราว
    client.handler.enforce_csrf_checks = True
    
    # 1. Arrange: เตรียมข้อมูลสำหรับการล็อกอิน
    login_url = reverse('users:login')

    # 2. Act: ส่งคำขอ POST เพื่อล็อกอินโดยไม่มี CSRF token
    login_response = client.post(login_url, {
        'username': new_staff.username,
        'password': '123456789'
    })

    # 3. Assert (การตรวจสอบเมื่อล็อกอินล้มเหลว)
    # 3.1 ตรวจสอบว่าระบบตอบกลับด้วย HTTP 403 Forbidden
    assert login_response.status_code == 403
    
    # 3.2 ตรวจสอบว่าไม่มี session ถูกสร้างขึ้น
    assert '_auth_user_id' not in client.session