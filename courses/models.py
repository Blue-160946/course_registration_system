from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from users.models import Profile
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import datetime, date

class Faculty(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="ชื่อคณะ")
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="ชื่อภาควิชา")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="departments", verbose_name="สังกัดคณะ")
    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="ชื่อสาขาวิชา")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="branches", verbose_name="สังกัดภาควิชา")
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
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES, verbose_name="ภาคเรียน")
    start_date = models.DateField(verbose_name="วันเปิดภาคเรียน")
    end_date = models.DateField(verbose_name="วันสิ้นสุดภาคเรียน")
    
    def clean(self):
        # 1. ตรวจสอบว่า end_date ไม่ได้มาก่อน start_date
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'วันสิ้นสุดภาคเรียนต้องอยู่หลังวันเปิดภาคเรียน'})

    def __str__(self):
        return f"ปีการศึกษา {self.year} - {self.get_semester_display()}"

    class Meta:
        unique_together = ('year', 'semester') # ห้ามมีปีและเทอมซ้ำกัน
    
class Room(models.Model):
    """เก็บข้อมูลห้องเรียน"""
    building = models.CharField(max_length=100, verbose_name="ชื่อตึก")
    room_number = models.CharField(max_length=20, verbose_name="เลขห้อง")

    def __str__(self):
        return f"{self.building} - ห้อง {self.room_number}"

    class Meta:
        # ป้องกันการสร้างห้องซ้ำในตึกเดียวกัน
        unique_together = ('building', 'room_number')
        

class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="courses", verbose_name="ภาควิชา", null=True, blank=True)
    credits = models.PositiveSmallIntegerField(
        default=3, 
        verbose_name="หน่วยกิต",
        validators=[
            MinValueValidator(1, message="หน่วยกิตต้องมีค่าอย่างน้อย 1"),
            MaxValueValidator(9, message="หน่วยกิตต้องมีค่าไม่เกิน 9")
        ]
    )
    is_active = models.BooleanField(default=True, verbose_name="สถานะเปิดใช้งาน")
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
    course = models.ForeignKey(Course, related_name='sections', on_delete=models.CASCADE, verbose_name="รายวิชา")
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
    
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="sections", verbose_name="ภาคเรียน")
    
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
    def __str__(self):
        return f"{self.course.code} - Section {self.section_number}"
    
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
        
class ClassTime(models.Model):
    
    DAY_CHOICES = [
    ('MON', 'วันจันทร์'), ('TUE', 'วันอังคาร'), ('WED', 'วันพุธ'),
    ('THU', 'วันพฤหัสบดี'), ('FRI', 'วันศุกร์'), ('SAT', 'วันเสาร์'), ('SUN', 'วันอาทิตย์'),
    ]

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="class_times")
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def clean(self):
        super().clean()
        if self.start_time and self.end_time:
            # ตรวจสอบว่า end_time ไม่ได้มาก่อน start_time
            if self.end_time <= self.start_time:
                raise ValidationError({'end_time': 'เวลาเลิกเรียนต้องอยู่หลังเวลาเริ่มเรียน'})
            
            # ตรวจสอบว่าเวลาเรียนไม่เกิน 4 ชั่วโมงต่อคาบ
            duration = (
                datetime.combine(date.today(), self.end_time) - 
                datetime.combine(date.today(), self.start_time)
            ).seconds / 3600  # แปลงเป็นชั่วโมง
            
            if duration > 4:
                raise ValidationError('ระยะเวลาเรียนต้องไม่เกิน 4 ชั่วโมงต่อคาบ')

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
    