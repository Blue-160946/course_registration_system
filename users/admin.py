from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'โปรไฟล์'
    fieldsets = (
        ('ประเภทผู้ใช้', {'fields': ('user_type',)}),
        ('ข้อมูลพื้นฐาน', {'fields': ('name_title','first_name_th', 'last_name_th', 'gender','date_of_birth', 'phone_number', 'address'), 'classes': ('collapse',)}),
        ('ข้อมูลนิสิต', {'fields': ('student_id', 'branch', 'student_status'), 'classes': ('collapse',)}),
        ('ข้อมูลอาจารย์', {'fields': ('acdemic_title', 'department'), 'classes': ('collapse',)}),
        ('ข้อมูลเจ้าหน้าที่', {'fields': ('job_title',), 'classes': ('collapse',)}),
    )

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('profile__user_type', 'username', 'profile__first_name_th', 'profile__last_name_th', 'is_staff')
    list_filter = ('profile__user_type', 'is_staff', 'is_active')
    

# ยกเลิกการลงทะเบียน UserAdmin เดิมและลงทะเบียนใหม่ด้วย UserAdmin ที่เราปรับแต่ง
admin.site.unregister(User)
admin.site.register(User, UserAdmin)