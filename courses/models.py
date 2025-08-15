from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from users.models import Profile
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import datetime, date

class Faculty(models.Model):
    thai_validator = RegexValidator(
        regex=r'^[ก-์\s]+$',
        message='กรุณาป้อนชื่อคณะเป็นภาษาไทยเท่านั้น'
    )
    name = models.CharField(
        max_length=200, 
        unique=True, 
        verbose_name="ชื่อคณะ",
        validators=[thai_validator]
    )
    
    def clean(self):
        super().clean()
        if not self.name:
            raise ValidationError({'name': 'กรุณากรอกชื่อคณะ'})
        if len(self.name.strip()) < 2:
            raise ValidationError({'name': 'ชื่อคณะต้องมีความยาวอย่างน้อย 2 ตัวอักษร'})
            
    def __str__(self):
        return self.name

class Department(models.Model):
    thai_validator = RegexValidator(
        regex=r'^[ก-์\s]+$',
        message='กรุณาป้อนชื่อภาควิชาเป็นภาษาไทยเท่านั้น'
    )
    name = models.CharField(
        max_length=200, 
        unique=True, 
        verbose_name="ชื่อภาควิชา",
        validators=[thai_validator]
    )
    faculty = models.ForeignKey(
        Faculty, 
        on_delete=models.CASCADE, 
        related_name="departments", 
        verbose_name="สังกัดคณะ"
    )
    
    def clean(self):
        super().clean()
        if not self.name:
            raise ValidationError({'name': 'กรุณากรอกชื่อภาควิชา'})
        if len(self.name.strip()) < 2:
            raise ValidationError({'name': 'ชื่อภาควิชาต้องมีความยาวอย่างน้อย 2 ตัวอักษร'})
        if not self.faculty:
            raise ValidationError({'faculty': 'กรุณาเลือกคณะ'})
            
    def __str__(self):
        return self.name

class Branch(models.Model):
    thai_validator = RegexValidator(
        regex=r'^[ก-์\s]+$',
        message='กรุณาป้อนชื่อสาขาวิชาเป็นภาษาไทยเท่านั้น'
    )
    name = models.CharField(
        max_length=200, 
        unique=True, 
        verbose_name="ชื่อสาขาวิชา",
        validators=[thai_validator]
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name="branches", 
        verbose_name="สังกัดภาควิชา"
    )
    
    def clean(self):
        super().clean()
        if not self.name:
            raise ValidationError({'name': 'กรุณากรอกชื่อสาขาวิชา'})
        if len(self.name.strip()) < 2:
            raise ValidationError({'name': 'ชื่อสาขาวิชาต้องมีความยาวอย่างน้อย 2 ตัวอักษร'})
        if not self.department:
            raise ValidationError({'department': 'กรุณาเลือกภาควิชา'})
            
    def __str__(self):
        return self.name
    
class Semester(models.Model):
    """เก็บข้อมูลปีการศึกษาและภาคเรียน"""
    SEMESTER_CHOICES = [
        (1, 'ภาคเรียนที่ 1'),
        (2, 'ภาคเรียนที่ 2'),
        (3, 'ภาคเรียนฤดูร้อน'),
    ]

    year = models.PositiveSmallIntegerField(
        verbose_name="ปีการศึกษา (พ.ศ.)",
        validators=[MinValueValidator(2560, message="ปีการศึกษาต้องไม่เก่ากว่าปี 2560")]
    )
    semester = models.PositiveSmallIntegerField(
        choices=SEMESTER_CHOICES, 
        verbose_name="ภาคเรียน"
    )
    start_date = models.DateField(
        verbose_name="วันเปิดภาคเรียน"
    )
    end_date = models.DateField(
        verbose_name="วันสิ้นสุดภาคเรียน"
    )
    
    def clean(self):
        super().clean()
        if not self.year:
            raise ValidationError({'year': 'กรุณากรอกปีการศึกษา'})
        if not self.semester:
            raise ValidationError({'semester': 'กรุณาเลือกภาคเรียน'})
        if not self.start_date:
            raise ValidationError({'start_date': 'กรุณากรอกวันเปิดภาคเรียน'})
        if not self.end_date:
            raise ValidationError({'end_date': 'กรุณากรอกวันสิ้นสุดภาคเรียน'})
            
        # ตรวจสอบปีการศึกษา
        current_year = datetime.now().year + 543  # แปลงเป็น พ.ศ.
        if self.year > current_year + 1:
            raise ValidationError({'year': 'ไม่สามารถสร้างภาคเรียนล่วงหน้าเกิน 1 ปีการศึกษา'})
            
        # ตรวจสอบวันที่
        if self.start_date and self.end_date:
            # ตรวจสอบว่า end_date ไม่ได้มาก่อน start_date
            if self.end_date < self.start_date:
                raise ValidationError({'end_date': 'วันสิ้นสุดภาคเรียนต้องอยู่หลังวันเปิดภาคเรียน'})
                
            # ตรวจสอบระยะเวลาภาคเรียน
            semester_duration = (self.end_date - self.start_date).days
            if semester_duration < 180:
                raise ValidationError('ระยะเวลาภาคเรียนต้องไม่น้อยกว่า 180 วัน')
            
    def __str__(self):
        return f"ปีการศึกษา {self.year} - {self.get_semester_display()}"

    class Meta:
        unique_together = ('year', 'semester') # ห้ามมีปีและเทอมซ้ำกัน
    
class Room(models.Model):
    """เก็บข้อมูลห้องเรียน"""
    building_validator = RegexValidator(
        regex=r'^[ก-์A-Za-z0-9\s\-]+$',
        message='ชื่อตึกต้องประกอบด้วยตัวอักษรภาษาไทย ภาษาอังกฤษ ตัวเลข และเครื่องหมาย - เท่านั้น'
    )
    room_number_validator = RegexValidator(
        regex=r'^[A-Za-z0-9\-]+$',
        message='เลขห้องต้องประกอบด้วยตัวอักษรภาษาอังกฤษ ตัวเลข และเครื่องหมาย - เท่านั้น'
    )
    building = models.CharField(
        max_length=100, 
        verbose_name="ชื่อตึก",
        validators=[building_validator]
    )
    room_number = models.CharField(
        max_length=20, 
        verbose_name="เลขห้อง",
        validators=[room_number_validator]
    )

    def clean(self):
        super().clean()
        if not self.building:
            raise ValidationError({'building': 'กรุณากรอกชื่อตึก'})
        if not self.room_number:
            raise ValidationError({'room_number': 'กรุณากรอกเลขห้อง'})
        if len(self.building.strip()) < 2:
            raise ValidationError({'building': 'ชื่อตึกต้องมีความยาวอย่างน้อย 2 ตัวอักษร'})
        if len(self.room_number.strip()) < 1:
            raise ValidationError({'room_number': 'เลขห้องต้องมีความยาวอย่างน้อย 1 ตัวอักษร'})

    def __str__(self):
        return f"{self.building} - ห้อง {self.room_number}"

    class Meta:
        # ป้องกันการสร้างห้องซ้ำในตึกเดียวกัน
        unique_together = ('building', 'room_number')
        

class Course(models.Model):
    department = models.ForeignKey(
        Department, 
        on_delete=models.PROTECT, 
        related_name="courses", 
        verbose_name="ภาควิชา", 
        null=True, 
        blank=True
    )
    credits = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="หน่วยกิต",
        validators=[
            MinValueValidator(1, message="หน่วยกิตต้องมีค่าอย่างน้อย 1"),
            MaxValueValidator(9, message="หน่วยกิตต้องมีค่าไม่เกิน 9")
        ]
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="สถานะเปิดใช้งาน"
    )
    code = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name="รหัสวิชา",
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',
                message='รหัสวิชาต้องเป็นตัวเลข 6 หลัก'
            )
        ]
    )
    name = models.CharField(
        max_length=200, 
        verbose_name="ชื่อวิชา",
        validators=[
            RegexValidator(
                regex=r'^[ก-์A-Za-z0-9\s\-(),]+$',
                message='ชื่อวิชาต้องประกอบด้วยตัวอักษรภาษาไทย ภาษาอังกฤษ ตัวเลข และเครื่องหมาย -(),เท่านั้น'
            )
        ]
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="คำอธิบายวิชา",
        validators=[
            RegexValidator(
                regex=r'^[ก-์A-Za-z0-9\s\-(),.]+$',
                message='คำอธิบายวิชาต้องประกอบด้วยตัวอักษรภาษาไทย ภาษาอังกฤษ ตัวเลข และเครื่องหมาย -(),.เท่านั้น'
            )
        ]
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

class Section(models.Model):
    course = models.ForeignKey(
        Course, 
        related_name='sections', 
        on_delete=models.CASCADE, 
        verbose_name="รายวิชา"
    )
    section_number = models.CharField(
        max_length=3, 
        verbose_name="กลุ่มเรียน (Sec)",
        validators=[
            RegexValidator(
                regex=r'^[1-9][0-9]?$',
                message='กรุณากรอกหมายเลขกลุ่มเรียนเป็นตัวเลข 1-99'
            )
        ]
    )
    capacity = models.PositiveIntegerField(
        default=30, 
        verbose_name="จำนวนที่รับ",
        validators=[
            MinValueValidator(1, message="จำนวนที่รับต้องมีค่าอย่างน้อย 1"),
            MaxValueValidator(200, message="จำนวนที่รับต้องไม่เกิน 200 คน")
        ]
    )
    semester = models.ForeignKey(
        Semester, 
        on_delete=models.PROTECT, 
        related_name="sections", 
        verbose_name="ภาคเรียน"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL, # ถ้าห้องถูกลบ Section จะยังอยู่แต่ไม่มีห้อง
        null=True,
        blank=True,
        verbose_name="ห้องเรียน"
    )
    instructors = models.ManyToManyField(
        User,
        related_name='taught_sections',
        verbose_name="อาจารย์ผู้สอน",
        limit_choices_to={'profile__user_type': Profile.UserType.INSTRUCTOR},
        blank=True  # ใช้ blank=True สำหรับ ManyToManyField
    )
    students = models.ManyToManyField(
        User, 
        related_name='enrolled_sections', 
        blank=True,
        verbose_name="นิสิตที่ลงทะเบียน"
    )
    
    def clean(self):
        super().clean()
            
        # ตรวจสอบ course เฉพาะเมื่อมีการบันทึกแล้ว
        if self.pk and not self.course_id:
            raise ValidationError({'course': 'กรุณาเลือกรายวิชา'})
            
        # ตรวจสอบว่าจำนวนนิสิตที่ลงทะเบียนต้องไม่เกินความจุ
        if hasattr(self, 'students'):
            if self.get_enrolled_count() > self.capacity:
                raise ValidationError('จำนวนนิสิตที่ลงทะเบียนเกินความจุของกลุ่มเรียน')
    
    def get_enrolled_count(self):
        return self.students.count()

    def is_full(self):
        return self.get_enrolled_count() >= self.capacity

    # --- เพิ่ม property นี้เข้าไป ---
    @property
    def available_seats(self):
        """คำนวณจำนวนที่นั่งที่เหลือ"""
        return self.capacity - self.get_enrolled_count()

    class Meta:
        unique_together = ('course', 'semester', 'section_number')
        
    def __str__(self):
        return f"{self.course.code} - Section {self.section_number}"
        
class ClassTime(models.Model):
    
    DAY_CHOICES = [
    ('MON', 'วันจันทร์'), ('TUE', 'วันอังคาร'), ('WED', 'วันพุธ'),
    ('THU', 'วันพฤหัสบดี'), ('FRI', 'วันศุกร์'), ('SAT', 'วันเสาร์'), ('SUN', 'วันอาทิตย์'),
    ]

    section = models.ForeignKey(
        Section, 
        on_delete=models.CASCADE,
        verbose_name="กลุ่มเรียน",
        related_name="class_times"
    )
    day = models.CharField(
        max_length=3, 
        choices=DAY_CHOICES,
        verbose_name="วัน",
    )
    start_time = models.TimeField(
        verbose_name="เวลาเริ่มเรียน"
    )
    end_time = models.TimeField(
        verbose_name="เวลาเลิกเรียน"
    )
    
    def clean(self):
        super().clean()
        if self.start_time and self.end_time:
            # ตรวจสอบว่า end_time ไม่ได้มาก่อน start_time
            if self.end_time <= self.start_time:
                raise ValidationError({'end_time': 'เวลาเลิกเรียนต้องอยู่หลังเวลาเริ่มเรียน'})
            
            # ตรวจสอบว่าเวลาเรียนไม่เกิน 2 ชั่วโมงต่อคาบ
            duration = (
                datetime.combine(date.today(), self.end_time) - 
                datetime.combine(date.today(), self.start_time)
            ).seconds / 3600  # แปลงเป็นชั่วโมง
            
            if duration > 2:
                raise ValidationError('ระยะเวลาเรียนต้องไม่เกิน 2 ชั่วโมงต่อคาบ')

            # ตรวจสอบการซ้ำซ้อนของเวลาเรียนในวันเดียวกัน
            if self.section_id:  # ตรวจสอบเฉพาะเมื่อมี section แล้ว
                overlapping_times = ClassTime.objects.filter(
                    section__semester=self.section.semester,
                    day=self.day
                ).exclude(id=self.id)  # ไม่นับตัวเอง

                for time in overlapping_times:
                    if (
                        (self.start_time <= time.start_time <= self.end_time) or
                        (self.start_time <= time.end_time <= self.end_time) or
                        (time.start_time <= self.start_time and time.end_time >= self.end_time)
                    ):
                        # ตรวจสอบว่ามีการใช้ห้องซ้ำกันหรือไม่
                        if self.section.room and self.section.room == time.section.room:
                            raise ValidationError(
                                f'ห้อง {self.section.room} ถูกใช้งานในช่วงเวลานี้แล้ว ' +
                                f'โดยวิชา {time.section.course.code} กลุ่ม {time.section.section_number}'
                            )

                        # ตรวจสอบว่าอาจารย์สอนซ้ำซ้อนหรือไม่
                        if any(instructor in time.section.instructors.all() 
                              for instructor in self.section.instructors.all()):
                            raise ValidationError(
                                'มีอาจารย์ในกลุ่มเรียนนี้มีตารางสอนซ้ำซ้อนกับ ' +
                                f'วิชา {time.section.course.code} กลุ่ม {time.section.section_number}'
                            )

    def __str__(self):
        return f"{self.section.course.code} Sec {self.section.section_number} ({self.get_day_display()} {self.start_time})"
    