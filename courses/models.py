from django.db import models
from django.contrib.auth.models import User
from users.models import Profile

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

    year = models.PositiveSmallIntegerField(verbose_name="ปีการศึกษา (พ.ศ.)")
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES, verbose_name="ภาคเรียน")
    start_date = models.DateField(verbose_name="วันเปิดภาคเรียน")
    end_date = models.DateField(verbose_name="วันสิ้นสุดภาคเรียน")

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
    credits = models.PositiveSmallIntegerField(default=3, verbose_name="หน่วยกิต")
    is_active = models.BooleanField(default=True, verbose_name="สถานะเปิดใช้งาน")
    code = models.CharField(max_length=10, unique=True, verbose_name="รหัสวิชา")
    name = models.CharField(max_length=200, verbose_name="ชื่อวิชา")
    description = models.TextField(blank=True, null=True, verbose_name="คำอธิบายวิชา")
    def __str__(self):
        return f"{self.code} - {self.name}"

class Section(models.Model):
    course = models.ForeignKey(Course, related_name='sections', on_delete=models.CASCADE, verbose_name="รายวิชา")
    section_number = models.CharField(max_length=5, verbose_name="กลุ่มเรียน (Sec)")
    capacity = models.PositiveIntegerField(default=30, verbose_name="จำนวนที่รับ")
    
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
        User, related_name='enrolled_sections', blank=True,
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

    def __str__(self):
        return f"{self.section.course.code} Sec {self.section.section_number} ({self.get_day_display()} {self.start_time})"
    

