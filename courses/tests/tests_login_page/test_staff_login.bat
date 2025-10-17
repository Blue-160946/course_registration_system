# course_registration_system/users/tests/test_staff_login_view.py
import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse
from types import SimpleNamespace

import users.views as user_views

User = get_user_model()


def _patch_auth_form_valid(monkeypatch):
    class DummyAuthForm:
        def __init__(self, request=None, data=None):
            data = data or {}
            self.cleaned_data = {
                'username': data.get('username'),
                'password': data.get('password'),
            }

        def is_valid(self):
            return True

    monkeypatch.setattr(user_views, 'AuthenticationForm', DummyAuthForm)


def _patch_authenticate(monkeypatch, return_value):
    calls = []

    def fake_authenticate(*args, **kwargs):
        calls.append(kwargs)
        return return_value

    monkeypatch.setattr(user_views, 'authenticate', fake_authenticate)
    return calls


def _patch_login(monkeypatch):
    calls = []

    def fake_login(request, user):
        calls.append(user)

    monkeypatch.setattr(user_views, 'login', fake_login)
    return calls


@pytest.mark.django_db
def test_staff_login_redirects_authenticated_user(client):
    user = User.objects.create_user(username='staffer', password='secret123')
    client.force_login(user)

    response = client.get(reverse('users:login'))

    assert response.status_code == 302
    assert response.url == reverse('core:index')


@pytest.mark.django_db
def test_staff_login_invalid_form_shows_error_message(client):
    response = client.post(reverse('users:login'), {'username': 'only_username'})

    assert response.status_code == 200
    assert any(t.name == 'users/login.html' for t in response.templates)
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง" in messages


@pytest.mark.django_db
def test_staff_login_staff_user_redirects_to_course_list(client, monkeypatch):
    staff_user = User.objects.create_user(username='staff', password='pass123', is_staff=True)
    _patch_auth_form_valid(monkeypatch)
    auth_calls = _patch_authenticate(monkeypatch, staff_user)
    login_calls = _patch_login(monkeypatch)

    response = client.post(reverse('users:login'), {'username': 'staff', 'password': 'pass123'})

    assert response.status_code == 302
    assert response.url == reverse('courses:course-list')
    assert auth_calls == [{'username': 'staff', 'password': 'pass123'}]
    assert login_calls == [staff_user]


@pytest.mark.django_db
def test_staff_login_student_user_redirects_to_public_section_list(client, monkeypatch):
    student_user = User.objects.create_user(username='student', password='pass123')
    student_user.profile = SimpleNamespace(user_type='STUDENT')

    _patch_auth_form_valid(monkeypatch)
    auth_calls = _patch_authenticate(monkeypatch, student_user)
    login_calls = _patch_login(monkeypatch)

    response = client.post(reverse('users:login'), {'username': 'student', 'password': 'pass123'})

    assert response.status_code == 302
    assert response.url == reverse('courses:public-section-list')
    assert auth_calls == [{'username': 'student', 'password': 'pass123'}]
    assert login_calls == [student_user]


@pytest.mark.django_db
def test_staff_login_disallowed_user_shows_permission_error(client, monkeypatch):
    other_user = User.objects.create_user(username='outsider', password='pass123')

    _patch_auth_form_valid(monkeypatch)
    _patch_authenticate(monkeypatch, other_user)
    login_calls = _patch_login(monkeypatch)

    response = client.post(reverse('users:login'), {'username': 'outsider', 'password': 'pass123'})

    assert response.status_code == 200
    assert any(t.name == 'users/login.html' for t in response.templates)
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "คุณไม่มีสิทธิ์เข้าใช้งานในส่วนนี้" in messages
    assert login_calls == []


@pytest.mark.django_db
def test_staff_login_invalid_credentials_show_error(client, monkeypatch):
    _patch_auth_form_valid(monkeypatch)
    _patch_authenticate(monkeypatch, None)
    login_calls = _patch_login(monkeypatch)

    response = client.post(reverse('users:login'), {'username': 'ghost', 'password': 'wrong'})

    assert response.status_code == 200
    messages = [m.message for m in get_messages(response.wsgi_request)]
    assert "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง" in messages
    assert login_calls == []
