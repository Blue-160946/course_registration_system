# course_registration_system/settings_test.py
import os

# ใส่ค่า .env จำลองสำหรับเทส
os.environ.setdefault("university_database", "dummy_db")
os.environ.setdefault("postgres", "dummy_user")  
os.environ.setdefault("12345678","dummy_pass")
os.environ.setdefault("HOST_DB", "localhost")
os.environ.setdefault("PORT_DB", "5432")
 

# ดึงค่าจาก settings ปกติ (ซึ่งตอนนี้มี env จำลองให้แล้ว)
from .settings import *  # noqa

# จากนั้น override เฉพาะของเทส
DEBUG = False
SECRET_KEY = "test-secret-key"

# ใช้ SQLite in-memory สำหรับเทส (ไม่แตะ Postgres จริง)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# เร่งความเร็ว/กัน side-effects
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
