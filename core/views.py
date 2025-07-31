# core/views.py
from django.shortcuts import render
from django.utils import timezone
from courses.models import Section, Semester

def index(request):
    # View สำหรับหน้าแรกของเว็บไซต์
    # 1. ตรวจสอบเทอมปัจจุบัน
    current_date = timezone.now().date()
    current_semester = Semester.objects.filter(start_date__lte=current_date, end_date__gte=current_date).first() # ดึงเทอมที่มีวันที่ปัจจุบันอยู่ในช่วงเริ่มต้นและสิ้นสุด

    # 2. ดึงข้อมูล Section ที่อยู่ในเทอมปัจจุบัน (ถ้ามี)
    sections = []
    if current_semester:
        sections = Section.objects.filter(
            semester=current_semester, # ดึงเฉพาะเทอมปัจจุบัน
            course__is_active=True # ดึงเฉพาะวิชาที่ยังเปิดใช้งาน
        ).order_by('course__code')[:6] # เรียงตามรหัสวิชาและจำกัดแค่ 6 รายการ

    context = {
        'sections': sections,
        'current_semester': current_semester,
    }
    return render(request, 'core/index.html', context)