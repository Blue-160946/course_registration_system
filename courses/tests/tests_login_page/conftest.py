# conftest.py
import pytest
import factory

from courses.tests.tests_login_page.factories import (
    UserFactory, ProfileFactory, DepartmentFactory
)

from users.models import Profile

@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def profile_factory():
    return ProfileFactory

@pytest.fixture
def department_factory():
    return DepartmentFactory


# Fixtures สำหรับสร้าง User แต่ละประเภท
@pytest.fixture
def new_staff(profile_factory):
    """สร้าง Profile และ User ที่เป็น Staff สำหรับการทดสอบ"""
    profile = profile_factory(
        user__username='admin',
        job_title='เจ้าหน้าที่',
        user_type=Profile.UserType.STAFF,
        user__is_staff=True,
    )
    return profile.user

@pytest.fixture
def new_student(profile_factory):
    """สร้าง Profile และ User ที่เป็น Student สำหรับการทดสอบ"""
    profile = profile_factory(
        user__username='65313037',
        user_type=Profile.UserType.STUDENT,
        user__is_staff=False,
    )
    return profile.user