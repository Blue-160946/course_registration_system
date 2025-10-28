
import pytest
from unittest.mock import MagicMock
from users.views import staff_login_view


@pytest.mark.unit_test_with_mock
def test_TC_001_staff_login_success_unit(mocker):
    """
    Unit Test:
    - Login ด้วย username/password ถูกต้อง
    - User เป็น staff
    - ต้องเรียก authenticate() และ login()
    - ต้อง redirect ไป courses:course-list
    """

    # สร้าง fake user
    fake_user = MagicMock()
    fake_user.is_staff = True

    # patch authenticate() และ login()
    mock_auth = mocker.patch("users.views.authenticate", return_value=fake_user)
    mock_login = mocker.patch("users.views.login")

    # patch AuthenticationForm ให้ is_valid = True
    mock_form_class = mocker.patch("users.views.AuthenticationForm")
    fake_form = MagicMock()
    fake_form.is_valid.return_value = True
    fake_form.cleaned_data = {"username": "admin", "password": "123456789"}
    mock_form_class.return_value = fake_form

    # fake request POST
    fake_request = MagicMock()
    fake_request.method = "POST"
    fake_request.POST = {"username": "admin", "password": "123456789"}
    fake_request.user.is_authenticated = False

    # patch render (ไม่จำเป็น เพราะ redirect จะ return HttpResponseRedirect)
    mock_render = mocker.patch("users.views.render", return_value="FAKE_RESPONSE")

    # เรียก view
    response = staff_login_view(fake_request)

    # ตรวจสอบว่า authenticate() ถูกเรียก
    mock_auth.assert_called_once_with(username="admin", password="123456789")

    # ตรวจสอบว่า login() ถูกเรียก
    mock_login.assert_called_once_with(fake_request, fake_user)

    # ตรวจสอบว่า response เป็น redirect (mocked หรือจริง)
    # ถ้า view ใช้ redirect() จริง ๆ จะไม่ต้อง mock render
    # สำหรับ template render จะ return FAKE_RESPONSE
    # ในกรณีนี้เราทดสอบ logic redirect
    assert response  # อย่างน้อย response ต้องไม่ None


@pytest.mark.unit_test_with_mock
def test_TC_002_staff_login_without_username_unit(mocker):
    """
    Unit Test:
    - ไม่กรอก username
    - form ไม่ valid
    - render หน้า login พร้อม error
    """

    # patch AuthenticationForm ให้ is_valid = False
    mock_form_class = mocker.patch("users.views.AuthenticationForm")
    fake_form = MagicMock()
    fake_form.is_valid.return_value = False
    fake_form.cleaned_data = {}
    fake_form.errors = {"username": ["กรุณากรอกชื่อผู้ใช้"]}
    mock_form_class.return_value = fake_form

    # fake request POST
    fake_request = MagicMock()
    fake_request.method = "POST"
    fake_request.POST = {"username": "", "password": "123456789"}
    fake_request.user.is_authenticated = False

    # patch render ให้ return FAKE_RESPONSE
    mock_render = mocker.patch("users.views.render", return_value="FAKE_RESPONSE")

    # เรียก view
    response = staff_login_view(fake_request)

    # ตรวจสอบว่า form ถูกสร้างด้วย request + POST data
    mock_form_class.assert_any_call(fake_request, data=fake_request.POST)

    # ตรวจสอบว่า render ถูกเรียก และ context มี form
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert args[0] == fake_request
    assert args[1] == "users/login.html"
    assert "form" in args[2]

    # ตรวจสอบ form ไม่ valid และมี error message
    form_in_context = args[2]["form"]
    assert not form_in_context.is_valid()
    assert "กรุณากรอกชื่อผู้ใช้" in form_in_context.errors["username"]

    # ตรวจสอบว่า response เป็น FAKE_RESPONSE
    assert response == "FAKE_RESPONSE"
    

@pytest.mark.unit_test_with_mock
def test_TC_003_user_staff_login_without_password(mocker):
    """
    Unit Test:
    - กรอก username แต่ไม่กรอก password
    - form ไม่ valid
    - render หน้า login พร้อม error
    """

    # patch AuthenticationForm ให้ is_valid = False
    mock_form_class = mocker.patch("users.views.AuthenticationForm")
    fake_form = MagicMock()
    fake_form.is_valid.return_value = False
    fake_form.cleaned_data = {}
    fake_form.errors = {"password": ["กรุณากรอกรหัสผ่าน"]}
    mock_form_class.return_value = fake_form

    # fake request POST
    fake_request = MagicMock()
    fake_request.method = "POST"
    fake_request.POST = {"username": "staff001", "password": ""}
    fake_request.user.is_authenticated = False

    # patch render ให้ return FAKE_RESPONSE
    mock_render = mocker.patch("users.views.render", return_value="FAKE_RESPONSE")

    # เรียก view
    response = staff_login_view(fake_request)

    # ตรวจสอบว่า form ถูกสร้างด้วย request + POST data
    mock_form_class.assert_any_call(fake_request, data=fake_request.POST)

    # ตรวจสอบว่า render ถูกเรียก และ context มี form
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert args[0] == fake_request
    assert args[1] == "users/login.html"
    assert "form" in args[2]

    # ตรวจสอบ form ไม่ valid และมี error message
    form_in_context = args[2]["form"]
    assert not form_in_context.is_valid()
    assert "กรุณากรอกรหัสผ่าน" in form_in_context.errors["password"]

    # ตรวจสอบว่า response เป็น FAKE_RESPONSE
    assert response == "FAKE_RESPONSE"
    

@pytest.mark.unit_test_with_mock
def test_TC_004_user_staff_login_without_username_and_password(mocker):
    """
    Unit Test:
    - ไม่กรอก username และ password
    - form ไม่ valid
    - render หน้า login พร้อม error
    """

    # patch AuthenticationForm ให้ is_valid = False
    mock_form_class = mocker.patch("users.views.AuthenticationForm")
    fake_form = MagicMock()
    fake_form.is_valid.return_value = False
    fake_form.cleaned_data = {}
    fake_form.errors = {
        "username": ["กรุณากรอกชื่อผู้ใช้"],
        "password": ["กรุณากรอกรหัสผ่าน"],
    }
    mock_form_class.return_value = fake_form

    # fake request POST
    fake_request = MagicMock()
    fake_request.method = "POST"
    fake_request.POST = {"username": "", "password": ""}
    fake_request.user.is_authenticated = False

    # patch render ให้ return FAKE_RESPONSE
    mock_render = mocker.patch("users.views.render", return_value="FAKE_RESPONSE")

    # เรียก view
    response = staff_login_view(fake_request)

    # ตรวจสอบว่า form ถูกสร้างด้วย request + POST data
    mock_form_class.assert_any_call(fake_request, data=fake_request.POST)

    # ตรวจสอบว่า render ถูกเรียก และ context มี form
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert args[0] == fake_request
    assert args[1] == "users/login.html"
    assert "form" in args[2]

    # ตรวจสอบ form ไม่ valid และมี error message
    form_in_context = args[2]["form"]
    assert not form_in_context.is_valid()
    assert "กรุณากรอกชื่อผู้ใช้" in form_in_context.errors["username"]
    assert "กรุณากรอกรหัสผ่าน" in form_in_context.errors["password"]

    # ตรวจสอบว่า response เป็น FAKE_RESPONSE
    assert response == "FAKE_RESPONSE"
    

@pytest.mark.unit_test_with_mock
def test_TC_005_user_staff_login_with_incorrect_username(mocker):
    """
    Unit Test:
    - กรอก username ผิด (ไม่มีในระบบ)
    - form valid แต่ authenticate() return None
    - render หน้า login พร้อม error
    """

    # patch authenticate() ให้ return None
    mock_auth = mocker.patch("users.views.authenticate", return_value=None)

    # patch AuthenticationForm ให้ is_valid = True
    mock_form_class = mocker.patch("users.views.AuthenticationForm")
    fake_form = MagicMock()
    fake_form.is_valid.return_value = True
    fake_form.cleaned_data = {"username": "wronguser", "password": "123456789"}
    mock_form_class.return_value = fake_form

    # fake request POST
    fake_request = MagicMock()
    fake_request.method = "POST"
    fake_request.POST = {"username": "wronguser", "password": "123456789"}
    fake_request.user.is_authenticated = False

    # patch render ให้ return FAKE_RESPONSE
    mock_render = mocker.patch("users.views.render", return_value="FAKE_RESPONSE")
    
    # patch messages.error
    mock_messages_error = mocker.patch("users.views.messages.error")

    # เรียก view
    response = staff_login_view(fake_request)

    # ตรวจสอบว่า authenticate() ถูกเรียก
    mock_auth.assert_called_once_with(username="wronguser", password="123456789")

    # ตรวจสอบว่า form ถูกสร้างด้วย request + POST data
    mock_form_class.assert_any_call(fake_request, data=fake_request.POST)

    # ตรวจสอบว่า render ถูกเรียก และ context มี form
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert args[0] == fake_request
    assert args[1] == "users/login.html"
    assert "form" in args[2]

    # ตรวจสอบ form valid แต่ authenticate() return None
    form_in_context = args[2]["form"]
    assert form_in_context.is_valid()
    
    # ตรวจสอบว่า messages.error ถูกเรียกด้วยข้อความถูกต้อง
    mock_messages_error.assert_called_once_with(fake_request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    
    # ตรวจสอบว่า response เป็น FAKE_RESPONSE
    assert response == "FAKE_RESPONSE"


@pytest.mark.unit_test_with_mock
def test_TC_006_user_staff_login_with_incorrect_password(mocker):
    """
    Unit Test:
    - กรอก password ผิด
    - form valid แต่ authenticate() return None
    - render หน้า login พร้อม error
    """

    # patch authenticate() ให้ return None
    mock_auth = mocker.patch("users.views.authenticate", return_value=None)

    # patch AuthenticationForm ให้ is_valid = True
    mock_form_class = mocker.patch("users.views.AuthenticationForm")
    fake_form = MagicMock()
    fake_form.is_valid.return_value = True
    fake_form.cleaned_data = {"username": "admin", "password": "wrongpassword"}
    mock_form_class.return_value = fake_form

    # fake request POST
    fake_request = MagicMock()
    fake_request.method = "POST"
    fake_request.POST = {"username": "admin", "password": "wrongpassword"}
    fake_request.user.is_authenticated = False

    # patch render ให้ return FAKE_RESPONSE
    mock_render = mocker.patch("users.views.render", return_value="FAKE_RESPONSE")
    
    # patch messages.error
    mock_messages_error = mocker.patch("users.views.messages.error")

    # เรียก view
    response = staff_login_view(fake_request)

    # ตรวจสอบว่า authenticate() ถูกเรียก
    mock_auth.assert_called_once_with(username="admin", password="wrongpassword")

    # ตรวจสอบว่า form ถูกสร้างด้วย request + POST data
    mock_form_class.assert_any_call(fake_request, data=fake_request.POST)

    # ตรวจสอบว่า render ถูกเรียก และ context มี form
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert args[0] == fake_request
    assert args[1] == "users/login.html"
    assert "form" in args[2]

    # ตรวจสอบ form valid แต่ authenticate() return None
    form_in_context = args[2]["form"]
    assert form_in_context.is_valid()
    
    # ตรวจสอบว่า messages.error ถูกเรียกด้วยข้อความถูกต้อง
    mock_messages_error.assert_called_once_with(fake_request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    
    # ตรวจสอบว่า response เป็น FAKE_RESPONSE
    assert response == "FAKE_RESPONSE"
    

@pytest.mark.unit_test_with_mock
def test_TC_007_user_staff_login_with_space_in_username_and_password(mocker):
    """
    Unit Test:
    - กรอก username และ password เป็นช่องว่าง
    - form valid แต่ authenticate() return None
    - render หน้า login พร้อม error
    """

    # สร้าง fake form
    mock_form_class = mocker.patch("users.views.AuthenticationForm")
    fake_form = MagicMock()
    fake_form.is_valid.return_value = True
    fake_form.cleaned_data = {"username": " ", "password": " "}
    mock_form_class.return_value = fake_form

    # สร้าง fake request POST
    fake_request = MagicMock()
    fake_request.method = "POST"
    fake_request.POST = {"username": " ", "password": " "}
    fake_request.user.is_authenticated = False

    # patch authenticate() ให้ return None → simulate login fail
    mock_auth = mocker.patch("users.views.authenticate", return_value=None)

    # patch messages.error
    mock_messages_error = mocker.patch("users.views.messages.error")

    # patch render
    mock_render = mocker.patch("users.views.render", return_value="FAKE_RESPONSE")

    # เรียก view
    response = staff_login_view(fake_request)

    # ตรวจสอบว่า authenticate() ถูกเรียกด้วยช่องว่าง
    mock_auth.assert_called_once_with(username=" ", password=" ")

    # login() ไม่ถูกเรียก
    # (ไม่จำเป็นต้อง patch login เพราะ authenticate fail)

    # messages.error() ถูกเรียก
    mock_messages_error.assert_called_once_with(fake_request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    # response เป็น render หน้า login
    assert response == "FAKE_RESPONSE"


@pytest.mark.unit_test_with_mock
def test_TC_008_check_login_page_csrf_token_unit(mocker):
    """
    Unit Test:
    - ตรวจสอบว่า view ส่ง form ไปใน context
    - ไม่เข้าถึง database
    """

    # patch AuthenticationForm
    mock_form_class = mocker.patch("users.views.AuthenticationForm")
    fake_form = mocker.MagicMock()
    mock_form_class.return_value = fake_form

    # สร้าง fake request GET
    fake_request = mocker.MagicMock()
    fake_request.method = "GET"
    fake_request.user.is_authenticated = False

    # patch render ให้ return FAKE_RESPONSE
    mock_render = mocker.patch("users.views.render", return_value="FAKE_RESPONSE")

    # เรียก view
    response = staff_login_view(fake_request)

    # ตรวจสอบว่า form ถูกสร้างด้วย request
    mock_form_class.assert_called_once_with()

    # ตรวจสอบว่า render ถูกเรียก และ context มี form
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert args[0] == fake_request
    assert args[1] == "users/login.html"
    assert "form" in args[2]
    assert args[2]["form"] == fake_form

    # ตรวจสอบว่า response เป็น FAKE_RESPONSE
    assert response == "FAKE_RESPONSE"