from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.forms import ValidationError
from phonenumber_field.modelfields import PhoneNumberField

'''
class user models
fields:
username
password
first_name
last_name
email
is_staff
is_active
date_joined
last_login
'''

class Profile(models.Model):
    class UserType(models.TextChoices):
        STUDENT = 'STUDENT', 'นิสิต'
        INSTRUCTOR = 'INSTRUCTOR', 'อาจารย์'
        STAFF = 'STAFF', 'เจ้าหน้าที่'
        
    class StudentStatus(models.TextChoices):
        STUDYING = 'STUDYING', 'กำลังศึกษา'
        ON_LEAVE = 'ON_LEAVE', 'พักการเรียน'
        GRADUATED = 'GRADUATED', 'สำเร็จการศึกษา'
        
    class Gender(models.TextChoices):
        MALE = 'MALE', 'ชาย'
        FEMALE = 'FEMALE', 'หญิง'
        OTHER = 'OTHER', 'อื่นๆ'
        
    class AcademicTitle(models.TextChoices):
        PROFESSOR = 'PROFESSOR', 'ศาสตราจารย์'
        ASSOCIATE_PROFESSOR = 'ASSOCIATE_PROFESSOR', 'รองศาสตราจารย์'
        ASSISTANT_PROFESSOR = 'ASSISTANT_PROFESSOR', 'ผู้ช่วยศาสตราจารย์'
        LECTURER = 'LECTURER', 'อาจารย์'
        
    class JobTitle(models.TextChoices):
        REGISTRATION_OFFICER = 'REGISTRATION_OFFICER', 'เจ้าหน้าที่ทะเบียน'

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="ผู้ใช้")
    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.STUDENT, verbose_name="ประเภทผู้ใช้")
    
    thai_validator = RegexValidator(
    regex=r'^[\u0E00-\u0E7F]+$',
    message='กรุณาป้อนเป็นตัวอักษรภาษาไทยเท่านั้น'
    )
    
    student_id_validator = RegexValidator(
        regex=r'^\d{8}$', # บังคับให้เป็นตัวเลข 8 หลัก
        message='รหัสนิสิตต้องเป็นตัวเลข 8 หลัก'
    )
    
    #ข้อมูลพื้นฐาน
    first_name_th = models.CharField(
        max_length=100,
        validators=[thai_validator],
        blank=True, 
        verbose_name="ชื่อ (ภาษาไทย)")
    last_name_th = models.CharField(
        max_length=100,
        validators=[thai_validator], 
        blank=True,
        verbose_name="นามสกุล (ภาษาไทย)")
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True, verbose_name="เพศ")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="วันเกิด")
    phone_number = PhoneNumberField(null=True, blank=True, verbose_name="เบอร์โทรศัพท์", region ='TH')
    address = models.TextField(null=True, blank=True, verbose_name="ที่อยู่")
    
    # ข้อมูลเพิ่มเติมสำหรับเจ้าหน้าที่
    job_title = models.CharField(max_length=100, choices=JobTitle.choices, null=True, blank=True, verbose_name="ตำแหน่งงาน")
    
    # ข้อมูลเพิ่มเติมสำหรับนิสิต
    student_id = models.CharField(
        max_length=8, 
        validators=[student_id_validator],
        unique=True,
        null=True, 
        blank=True, 
        verbose_name="รหัสนิสิต")
    branch = models.ForeignKey('courses.Branch', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="สาขาวิชา")
    student_status = models.CharField(max_length=10, choices=StudentStatus.choices, default=StudentStatus.STUDYING, verbose_name="สถานะนิสิต")
    
    # ข้อมูลเพิ่มเติมสำหรับอาจารย์
    acdemic_title = models.CharField(max_length=50, choices=AcademicTitle.choices, null=True, blank=True, verbose_name="ตำแหน่งทางวิชาการ")
    department = models.ForeignKey('courses.Department', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ภาควิชา")

    def clean(self):
        """
        Custom validation logic สำหรับ Model ทั้งหมด
        """
        super().clean()
        # 1. ตรวจสอบว่าวันเกิดต้องไม่เป็นวันในอนาคต
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValidationError({'date_of_birth': 'วันเกิดต้องไม่เป็นวันในอนาคต'})

    def __str__(self):
        return self.user.username