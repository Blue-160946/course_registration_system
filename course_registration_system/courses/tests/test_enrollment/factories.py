import factory
from users.models import Profile
from django.contrib.auth.models import User
from courses.models import Faculty, Department, Branch, Course, Section, Semester, Room

# ---------------- Faculty ----------------
class FacultyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Faculty
    name = factory.Faker("word")  # ชื่อคณะเป็นภาษาไทยก็ได้

# ---------------- Department ----------------
class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department
    name = factory.Faker("word")
    faculty = factory.SubFactory(FacultyFactory)

# ---------------- Branch ----------------
class BranchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Branch
    name = factory.Faker("word")
    department = factory.SubFactory(DepartmentFactory)

# ---------------- Semester ----------------
class SemesterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Semester
    year = 2568
    semester = 1
    start_date = "2025-06-01"
    end_date = "2025-11-30"

# ---------------- Room ----------------
class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room
    building = "ตึก A"
    room_number = factory.Sequence(lambda n: f"{100+n}")

# ---------------- User & Profile ----------------
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "pass1234")

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
    user = factory.SubFactory(UserFactory)
    user_type = Profile.UserType.STUDENT
    student_id = factory.Sequence(lambda n: f"{65010000 + n}")
    branch = factory.SubFactory(BranchFactory)

# ---------------- Course ----------------
class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course
    code = factory.Sequence(lambda n: f"{100000+n}")  # 6 หลัก
    name = factory.Faker("sentence", nb_words=3)
    department = factory.SubFactory(DepartmentFactory)
    fee = 0
    credits = 3

# ---------------- Section ----------------
class SectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Section
    course = factory.SubFactory(CourseFactory)
    section_number = "1"
    capacity = 30
    semester = factory.SubFactory(SemesterFactory)
    room = factory.SubFactory(RoomFactory)
