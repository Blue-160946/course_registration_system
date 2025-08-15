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
        
    class NameTitle(models.TextChoices):
        MR = 'MR', 'นาย'
        MRS = 'MRS', 'นาง'
        MS = 'MS', 'นางสาว'
        DR = 'DR', 'ดร.'
        
    class AcademicTitle(models.TextChoices):
        PROFESSOR = 'PROFESSOR', 'ศาสตราจารย์'
        ASSOCIATE_PROFESSOR = 'ASSOCIATE_PROFESSOR', 'รองศาสตราจารย์'
        ASSISTANT_PROFESSOR = 'ASSISTANT_PROFESSOR', 'ผู้ช่วยศาสตราจารย์'
        LECTURER = 'LECTURER', 'อาจารย์'
        
    class JobTitle(models.TextChoices):
        REGISTRATION_OFFICER = 'REGISTRATION_OFFICER', 'เจ้าหน้าที่ทะเบียน'

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        verbose_name="ผู้ใช้")
    user_type = models.CharField(
        max_length=10, 
        choices=UserType.choices, 
        default=UserType.STUDENT, 
        verbose_name="ประเภทผู้ใช้")
    
    # Validators
    thai_validator = RegexValidator(
        regex=r'^[\u0E00-\u0E7F\s]+$',
        message='กรุณาป้อนเป็นตัวอักษรภาษาไทยเท่านั้น'
    )
    
    student_id_validator = RegexValidator(
        regex=r'^\d{8}$',
        message='รหัสนิสิตต้องเป็นตัวเลข 8 หลัก'
    )
    
    address_validator = RegexValidator(
        regex=r'^[ก-๙0-9/\s,.-]+$',
        message='ที่อยู่ต้องเป็นภาษาไทยและอักขระที่กำหนดเท่านั้น'
    )
    
    # ข้อมูลพื้นฐาน
    name_title = models.CharField(
        max_length=10, 
        choices=NameTitle.choices, 
        null=True, 
        blank=True, 
        verbose_name="คำนำหน้าชื่อ")
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
    gender = models.CharField(
        max_length=10, 
        choices=Gender.choices, 
        null=True, 
        blank=True, 
        verbose_name="เพศ")
    date_of_birth = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="วันเกิด")
    phone_number = PhoneNumberField(
        null=True, 
        blank=True, 
        verbose_name="เบอร์โทรศัพท์", 
        region ='TH')
    address = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="ที่อยู่",
        validators=[address_validator],
        help_text="กรอกที่อยู่เป็นภาษาไทย ใช้ตัวเลขและเครื่องหมาย /,.-"
    )
    
    # ข้อมูลเพิ่มเติมสำหรับเจ้าหน้าที่
    job_title = models.CharField(
        max_length=100, 
        choices=JobTitle.choices, 
        null=True, 
        blank=True, 
        verbose_name="ตำแหน่งงาน"
    )
    
    # ข้อมูลเพิ่มเติมสำหรับนิสิต
    student_id = models.CharField(
        max_length=8, 
        validators=[student_id_validator],
        unique=True,
        null=True, 
        blank=True, 
        verbose_name="รหัสนิสิต")
    branch = models.ForeignKey(
        'courses.Branch', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True, 
        verbose_name="สาขาวิชา")
    student_status = models.CharField(
        max_length=10, 
        null=True, 
        blank=True,
        choices=StudentStatus.choices,
        verbose_name="สถานะนิสิต")
    
    # ข้อมูลเพิ่มเติมสำหรับอาจารย์
    acdemic_title = models.CharField(
        max_length=50, 
        choices=AcademicTitle.choices, 
        null=True, 
        blank=True, 
        verbose_name="ตำแหน่งทางวิชาการ")
    department = models.ForeignKey(
        'courses.Department', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="ภาควิชา")

    def clean(self):
        
        super().clean()
        
        # 1. ตรวจสอบว่าวันเกิดต้องไม่เป็นวันในอนาคตและไม่เก่าเกินไป
        if self.date_of_birth:
            if self.date_of_birth > date.today():
                raise ValidationError({'date_of_birth': 'วันเกิดต้องไม่เป็นวันในอนาคต'})
            
            # คำนวณอายุ
            today = date.today()
            age = today.year - self.date_of_birth.year - \
                ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            
            if age < 15:
                raise ValidationError({'date_of_birth': 'อายุต้องไม่น้อยกว่า 15 ปี'})
            if age > 100:
                raise ValidationError({'date_of_birth': 'อายุต้องไม่เกิน 100 ปี'})

        # 2. ตรวจสอบข้อมูลตามประเภทผู้ใช้
        if self.user_type == self.UserType.STUDENT:
            # ตรวจสอบข้อมูลที่จำเป็นสำหรับนิสิต
            if not self.student_id:
                raise ValidationError({'student_id': 'นิสิตต้องมีรหัสนิสิต'})
            if not self.branch:
                raise ValidationError({'branch': 'นิสิตต้องระบุสาขาวิชา'})
            # เช็คว่าไม่มีข้อมูลที่ไม่เกี่ยวข้องกับนิสิต
            if self.acdemic_title or self.job_title:
                raise ValidationError('นิสิตไม่ควรมีข้อมูลตำแหน่งทางวิชาการหรือตำแหน่งงาน')

        elif self.user_type == self.UserType.INSTRUCTOR:
            # ตรวจสอบข้อมูลที่จำเป็นสำหรับอาจารย์
            if not self.department:
                raise ValidationError({'department': 'อาจารย์ต้องระบุภาควิชา'})
            if not self.acdemic_title:
                raise ValidationError({'acdemic_title': 'อาจารย์ต้องระบุตำแหน่งทางวิชาการ'})
            # เช็คว่าไม่มีข้อมูลที่ไม่เกี่ยวข้องกับอาจารย์
            if self.student_id or self.student_status or self.job_title:
                raise ValidationError('อาจารย์ไม่ควรมีข้อมูลรหัสนิสิต สถานะนิสิต หรือตำแหน่งงาน')

        elif self.user_type == self.UserType.STAFF:
            # ตรวจสอบข้อมูลที่จำเป็นสำหรับเจ้าหน้าที่
            if not self.job_title:
                raise ValidationError({'job_title': 'เจ้าหน้าที่ต้องระบุตำแหน่งงาน'})
            # เช็คว่าไม่มีข้อมูลที่ไม่เกี่ยวข้องกับเจ้าหน้าที่
            if self.student_id or self.student_status or self.acdemic_title:
                raise ValidationError('เจ้าหน้าที่ไม่ควรมีข้อมูลรหัสนิสิต สถานะนิสิต หรือตำแหน่งทางวิชาการ')

        # 3. ตรวจสอบชื่อภาษาไทย
        if self.first_name_th or self.last_name_th:
            if not (self.first_name_th and self.last_name_th):
                raise ValidationError('กรุณากรอกทั้งชื่อและนามสกุลภาษาไทย')

        # 4. ตรวจสอบที่อยู่
        if self.address and len(self.address.strip()) < 10:
            raise ValidationError({'address': 'ที่อยู่ต้องมีความยาวอย่างน้อย 10 ตัวอักษร'})

    def __str__(self):
        # แสดงชื่อภาษาไทยถ้ามี
        if self.first_name_th and self.last_name_th:
            return f"{self.first_name_th} {self.last_name_th}"
        return self.user.username