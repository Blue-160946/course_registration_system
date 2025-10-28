import random
from datetime import date

import factory
from factory import random as factory_random
from factory.django import DjangoModelFactory
import faker

from django.contrib.auth.models import User

from courses.models import (
    Branch,
    Course,
    Department,
    Faculty,
    Room,
    Section,
    Semester,
)
from users.models import Profile


TEST_SEED = 20251024

random.seed(TEST_SEED)
factory_random.reseed_random(TEST_SEED)
faker.Faker.seed(TEST_SEED)


class FacultyFactory(DjangoModelFactory):
    """???????????????????????????????????????????"""

    class Meta:
        model = Faculty
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"???????????{n + 1}")


class DepartmentFactory(DjangoModelFactory):
    """??????????????????"""

    class Meta:
        model = Department
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"???????{n + 1}")
    faculty = factory.SubFactory(FacultyFactory)


class BranchFactory(DjangoModelFactory):
    """???????????????"""

    class Meta:
        model = Branch
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"????{n + 1}")
    department = factory.SubFactory(DepartmentFactory)


class SemesterFactory(DjangoModelFactory):
    """???????????????????"""

    class Meta:
        model = Semester
        django_get_or_create = ("year", "semester")

    year = 2567
    semester = factory.Iterator([1, 2])

    @factory.lazy_attribute
    def start_date(self):
        if self.semester == 1:
            return date(2024, 1, 15)
        return date(2024, 8, 21)

    @factory.lazy_attribute
    def end_date(self):
        if self.semester == 1:
            return date(2024, 8, 20)
        return date(2025, 1, 10)


class RoomFactory(DjangoModelFactory):
    """????????????????????"""

    class Meta:
        model = Room

    building = factory.Sequence(lambda n: f"?????{n + 1}")
    room_number = factory.Sequence(lambda n: f"{100 + n}")


class UserFactory(DjangoModelFactory):
    """?????????????????????"""

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n + 1}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        password_value = extracted or "TestPass123!"
        obj.set_password(password_value)
        if create:
            obj.save()


class StudentFactory(DjangoModelFactory):
    """??????????????????????????"""

    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    user_type = Profile.UserType.STUDENT
    student_id = factory.Sequence(lambda n: f"{66000000 + n:08d}")
    branch = factory.SubFactory(BranchFactory)
    student_status = Profile.StudentStatus.STUDYING
    first_name_th = factory.Iterator(["?????", "????", "?????", "??????"])
    last_name_th = factory.Iterator(["???", "?????", "??????", "??????"])
    gender = Profile.Gender.MALE
    date_of_birth = date(2000, 1, 1)
    phone_number = "+66801234567"
    address = "123/45 Main Street, Sample District"


class CourseFactory(DjangoModelFactory):
    """??????????????????"""

    class Meta:
        model = Course

    department = factory.SubFactory(DepartmentFactory)
    credits = 3
    is_active = True
    code = factory.Sequence(lambda n: f"{100000 + n:06d}")
    name = factory.Sequence(lambda n: f"Introduction to Testing {n}")
    description = factory.LazyAttribute(lambda o: f"{o.name} description")
    fee = 1500


class SectionFactory(DjangoModelFactory):
    """???????????????????????????"""

    class Meta:
        model = Section

    course = factory.SubFactory(CourseFactory)
    section_number = factory.Sequence(lambda n: f"{(n % 98) + 1}")
    capacity = 30
    semester = factory.SubFactory(SemesterFactory)
    room = factory.SubFactory(RoomFactory)

    @factory.post_generation
    def instructors(obj, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            obj.instructors.set(extracted)


class EnrollmentFactory(DjangoModelFactory):
    """??????????????????????????????????? (Section.students.through)"""

    class Meta:
        model = Section.students.through

    section = factory.SubFactory(SectionFactory)
    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def ensure_student_profile(obj, create, extracted, **kwargs):
        if not create:
            return
        if not hasattr(obj.user, "profile"):
            StudentFactory(user=obj.user)
