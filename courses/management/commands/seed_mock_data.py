"""Create a small, repeatable set of demonstration data for local development."""

from datetime import date, time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from courses.models import Branch, ClassTime, Course, Department, Faculty, Room, Section, Semester
from payment.models import PaymentTransaction
from users.models import Profile


class Command(BaseCommand):
    help = "Create mock course-registration data. Running this command again is safe."

    password = "DemoPass123!"

    def handle(self, *args, **options):
        faculty, _ = Faculty.objects.get_or_create(name="คณะวิทยาศาสตร์")
        department, _ = Department.objects.get_or_create(
            name="ภาควิชาวิทยาการคอมพิวเตอร์", defaults={"faculty": faculty}
        )
        if department.faculty_id != faculty.id:
            department.faculty = faculty
            department.save(update_fields=["faculty"])

        branch, _ = Branch.objects.get_or_create(
            name="สาขาวิทยาการคอมพิวเตอร์", defaults={"department": department}
        )
        if branch.department_id != department.id:
            branch.department = department
            branch.save(update_fields=["department"])

        semester, _ = Semester.objects.get_or_create(
            year=2569,
            semester=1,
            defaults={"start_date": date(2026, 6, 8), "end_date": date(2026, 10, 4)},
        )

        rooms = {
            "lab": self._room("อาคารวิทยาศาสตร์", "LAB-101"),
            "lecture": self._room("อาคารวิทยาศาสตร์", "201"),
            "large": self._room("อาคารเรียนรวม", "301"),
        }

        staff = self._user("registrar", "เจ้าหน้าที่", "ทะเบียน", "registrar@example.test", is_staff=True)
        self._profile(
            staff,
            user_type=Profile.UserType.STAFF,
            name_title=Profile.NameTitle.MS,
            first_name_th="เจ้าหน้าที่",
            last_name_th="ทะเบียน",
            gender=Profile.Gender.FEMALE,
            date_of_birth=date(1987, 5, 12),
            phone_number="+66810000001",
            address="123 ถนนมหาวิทยาลัย แขวงปทุมวัน กรุงเทพมหานคร 10330",
            job_title=Profile.JobTitle.REGISTRATION_OFFICER,
        )

        instructors = [
            self._instructor("somchai", "สมชาย", "ใจดี", Profile.AcademicTitle.ASSISTANT_PROFESSOR, department),
            self._instructor("suda", "สุดา", "มั่นคง", Profile.AcademicTitle.LECTURER, department),
        ]
        students = [
            self._student("student_66000001", "66000001", "กิตติพงศ์", "สุขใจ", Profile.Gender.MALE, branch),
            self._student("student_66000002", "66000002", "พิมพ์ชนก", "แสงทอง", Profile.Gender.FEMALE, branch),
            self._student("student_66000003", "66000003", "ณัฐวุฒิ", "คำดี", Profile.Gender.MALE, branch),
            self._student("student_66000004", "66000004", "ชนากานต์", "วงศ์ดี", Profile.Gender.FEMALE, branch),
        ]

        courses = {
            "programming": self._course(department, "230101", "การเขียนโปรแกรมเบื้องต้น", 3, 1500),
            "database": self._course(department, "230201", "ระบบฐานข้อมูล", 3, 1500),
            "web": self._course(department, "230301", "การพัฒนาเว็บ", 3, 1500),
            "math": self._course(department, "230401", "คณิตศาสตร์ดิสครีต", 3, 0),
        }

        sections = {
            "programming": self._section(courses["programming"], semester, "1", 35, rooms["lab"], instructors[0]),
            "database": self._section(courses["database"], semester, "1", 30, rooms["lab"], instructors[1]),
            "web": self._section(courses["web"], semester, "1", 30, rooms["lecture"], instructors[0]),
            "math": self._section(courses["math"], semester, "1", 40, rooms["large"], instructors[1]),
        }

        self._class_time(sections["programming"], "MON", time(9), time(11))
        self._class_time(sections["programming"], "WED", time(9), time(11))
        self._class_time(sections["database"], "TUE", time(9), time(11))
        self._class_time(sections["database"], "THU", time(9), time(11))
        self._class_time(sections["web"], "MON", time(13), time(15))
        self._class_time(sections["web"], "WED", time(13), time(15))
        self._class_time(sections["math"], "TUE", time(13), time(15))
        self._class_time(sections["math"], "THU", time(13), time(15))

        enrollments = {
            "programming": students[:3],
            "database": students[:2],
            "web": [students[0], students[2], students[3]],
            "math": students,
        }
        for key, enrolled_students in enrollments.items():
            sections[key].students.add(*(profile.user for profile in enrolled_students))

        for profile, course in [
            (students[0], courses["programming"]),
            (students[1], courses["programming"]),
            (students[0], courses["database"]),
            (students[1], courses["database"]),
            (students[0], courses["web"]),
            (students[2], courses["web"]),
            (students[3], courses["web"]),
        ]:
            PaymentTransaction.objects.get_or_create(
                student=profile,
                course=course,
                defaults={
                    "amount": course.fee,
                    "status": "SUCCESS",
                    "transaction_id": f"MOCK-{profile.student_id}-{course.code}",
                },
            )

        self.stdout.write(self.style.SUCCESS(
            "Mock data ready: 1 faculty, 1 department, 1 branch, 4 courses, 4 sections, 4 students."
        ))
        self.stdout.write("Demo password for newly created accounts: DemoPass123!")

    def _user(self, username, first_name, last_name, email, is_staff=False):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": first_name, "last_name": last_name, "email": email, "is_staff": is_staff},
        )
        if created:
            user.set_password(self.password)
            user.save(update_fields=["password"])
        return user

    def _profile(self, user, **defaults):
        return Profile.objects.get_or_create(user=user, defaults=defaults)[0]

    def _instructor(self, username, first_name, last_name, academic_title, department):
        user = self._user(username, first_name, last_name, f"{username}@example.test")
        return self._profile(
            user,
            user_type=Profile.UserType.INSTRUCTOR,
            name_title=Profile.NameTitle.DR,
            first_name_th=first_name,
            last_name_th=last_name,
            gender=Profile.Gender.MALE if username == "somchai" else Profile.Gender.FEMALE,
            date_of_birth=date(1975, 1, 1),
            phone_number="+66810000002" if username == "somchai" else "+66810000003",
            address="123 ถนนมหาวิทยาลัย แขวงปทุมวัน กรุงเทพมหานคร 10330",
            acdemic_title=academic_title,
            department=department,
        )

    def _student(self, username, student_id, first_name, last_name, gender, branch):
        user = self._user(username, first_name, last_name, f"{username}@example.test")
        return self._profile(
            user,
            user_type=Profile.UserType.STUDENT,
            name_title=Profile.NameTitle.MR if gender == Profile.Gender.MALE else Profile.NameTitle.MS,
            first_name_th=first_name,
            last_name_th=last_name,
            gender=gender,
            date_of_birth=date(2005, 1, 1),
            phone_number=f"+66810000{student_id[-3:]}",
            address="123 ถนนมหาวิทยาลัย แขวงปทุมวัน กรุงเทพมหานคร 10330",
            student_id=student_id,
            branch=branch,
            student_status=Profile.StudentStatus.STUDYING,
        )

    @staticmethod
    def _room(building, room_number):
        return Room.objects.get_or_create(building=building, room_number=room_number)[0]

    @staticmethod
    def _course(department, code, name, credits, fee):
        return Course.objects.get_or_create(
            code=code,
            defaults={
                "department": department,
                "name": name,
                "credits": credits,
                "fee": fee,
                "description": f"รายวิชา{name}",
            },
        )[0]

    @staticmethod
    def _section(course, semester, section_number, capacity, room, instructor):
        section, _ = Section.objects.get_or_create(
            course=course,
            semester=semester,
            section_number=section_number,
            defaults={"capacity": capacity, "room": room},
        )
        section.instructors.add(instructor.user)
        return section

    @staticmethod
    def _class_time(section, day, start_time, end_time):
        ClassTime.objects.get_or_create(
            section=section,
            day=day,
            start_time=start_time,
            defaults={"end_time": end_time},
        )
