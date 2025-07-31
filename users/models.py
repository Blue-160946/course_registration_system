from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    class UserType(models.TextChoices):
        STUDENT = 'STUDENT', 'นิสิต'
        INSTRUCTOR = 'INSTRUCTOR', 'อาจารย์'
        STAFF = 'STAFF', 'เจ้าหน้าที่'
        
    class StudentStatus(models.TextChoices):
        STUDYING = 'STUDYING', 'กำลังศึกษา'
        ON_LEAVE = 'ON_LEAVE', 'พักการเรียน'
        GRADUATED = 'GRADUATED', 'สำเร็จการศึกษา'

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="ผู้ใช้")
    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.STUDENT, verbose_name="ประเภทผู้ใช้")
    
    # ข้อมูลเพิ่มเติมสำหรับเจ้าหน้าที่
    staff_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="ชื่อเจ้าหน้าที่")
    
    # ข้อมูลเพิ่มเติมสำหรับนิสิต
    student_id = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="รหัสนิสิต")
    student_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="ชื่อนิสิต")
    branch = models.ForeignKey('courses.Branch', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="สาขาวิชา")
    student_status = models.CharField(max_length=10, choices=StudentStatus.choices, default=StudentStatus.STUDYING, verbose_name="สถานะนิสิต")
    
    # ข้อมูลเพิ่มเติมสำหรับอาจารย์
    instructor_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="ชื่ออาจารย์")

    def __str__(self):
        return self.user.username