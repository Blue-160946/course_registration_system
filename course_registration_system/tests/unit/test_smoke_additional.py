import importlib


def test_core_tests_importable():
    """Smoke test: โมดูล core.tests import ได้"""
    assert importlib.import_module("core.tests") is not None


def test_payment_tests_importable():
    """Smoke test: โมดูล payment.tests import ได้"""
    assert importlib.import_module("payment.tests") is not None


def test_users_tests_importable():
    """Smoke test: โมดูล users.tests import ได้"""
    assert importlib.import_module("users.tests") is not None


def test_payment_views_importable():
    """Smoke test: payment.views import ได้โดยไม่เกิดข้อผิดพลาด"""
    assert importlib.import_module("payment.views") is not None
