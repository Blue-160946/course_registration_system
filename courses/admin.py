from django.contrib import admin
from .models import Faculty, Department, Branch, Course, Section, Room, Semester, ClassTime


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty')
    list_filter = ('faculty',)
    search_fields = ('name', 'faculty__name')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department__faculty', 'department')
    search_fields = ('name', 'department__name')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('building', 'room_number')
    list_filter = ('building',)
    search_fields = ('building', 'room_number')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_date', 'end_date')
    list_filter = ('year',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'credits', 'is_active')
    list_filter = ('is_active', 'department__faculty', 'department')
    search_fields = ('code', 'name', 'department__name')
    
class ClassTimeInline(admin.TabularInline):
    model = ClassTime
    extra = 1

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'semester', 'room', 'display_instructors')
    list_filter = ('semester', 'course__department__faculty', 'course', 'room__building')
    search_fields = ('course__name', 'course__code')
    filter_horizontal = ('students', 'instructors')
    inlines = [ClassTimeInline]

    def display_instructors(self, obj):
        return ", ".join([user.profile.instructor_name or user.username for user in obj.instructors.all()])
    
    display_instructors.short_description = 'อาจารย์ผู้สอน'
    
    def display_class_times(self, obj):
        return " | ".join([
            f"{ct.get_day_display()} {ct.start_time.strftime('%H:%M')}-{ct.end_time.strftime('%H:%M')}" 
            for ct in obj.class_times.all()
        ])
    display_class_times.short_description = 'วัน-เวลาเรียน'
