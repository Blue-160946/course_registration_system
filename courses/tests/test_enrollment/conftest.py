# tests/conftest.py
import pytest
from django.test import Client
from courses.tests.test_enrollment.factories import ProfileFactory, SectionFactory

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def student_profile():
    return ProfileFactory()

@pytest.fixture
def free_section():
    return SectionFactory()
