import pytest
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from courses.views import staff_required
from tests.factories import UserFactory


def dummy_view(request, *args, **kwargs):
    """วิวจำลองเพื่อทดสอบเดโคเรเตอร์"""
    return "ok"

@pytest.mark.unit
@pytest.mark.django_db
def test_staff_required_allows_staff_user():
    """ตรวจว่า user ที่เป็น staff ผ่านเข้าไปในวิวได้"""
    # Arrange
    wrapped = staff_required(dummy_view)
    request = RequestFactory().get("/")
    request.user = UserFactory(is_staff=True)

    # Act
    result = wrapped(request)

    # Assert
    assert result == "ok"

@pytest.mark.unit
@pytest.mark.django_db
def test_staff_required_blocks_non_staff():
    """ตรวจว่าผู้ใช้ทั่วไปถูกปฏิเสธด้วย PermissionDenied"""
    # Arrange
    wrapped = staff_required(dummy_view)
    request = RequestFactory().get("/")
    request.user = UserFactory(is_staff=False)

    # Act / Assert
    with pytest.raises(PermissionDenied):
        wrapped(request)
