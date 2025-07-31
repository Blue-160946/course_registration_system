from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Course, Section, Semester
from .forms import ClassTimeFormSet, CourseForm, SectionForm

# เช็คว่าผู้ใช้เป็น staff ก่อนเข้าถึง view
def staff_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

@login_required
@staff_required
def course_list(request):
    """แสดงรายการวิชาทั้งหมด"""
    courses = Course.objects.all().order_by('code') # เรียงตามรหัสวิชา
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
@staff_required
def course_add(request):
    """เพิ่มรายวิชาใหม่"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('courses:course-list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})


@login_required
@staff_required
def course_edit(request, pk):
    """แก้ไขรายวิชา"""
    course = get_object_or_404(Course, pk=pk) # ดึง Course ที่ต้องการแก้ไข
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses:course-list')
    else:
        form = CourseForm(instance=course)
    # ส่ง object ไปด้วยเพื่อให้ template รู้ว่ากำลัง 'แก้ไข'
    return render(request, 'courses/course_form.html', {'form': form, 'object': course})

@login_required
@staff_required
def course_delete(request, pk):
    """ลบรายวิชา"""
    course = get_object_or_404(Course, pk=pk) # ดึง Course ที่ต้องการลบ
    if request.method == 'POST':
        course.delete()
        return redirect('courses:course-list')
    return render(request, 'courses/course_confirm_delete.html', {'object': course})

@login_required
@staff_required
def section_list(request, course_pk):
    """แสดงรายการ Section ทั้งหมดของ Course ที่ระบุ"""
    course = get_object_or_404(Course, pk=course_pk)
    sections = Section.objects.filter(course=course).order_by('section_number') # เรียงตามหมายเลข Section
    context = {
        'course': course,
        'sections': sections,
    }
    return render(request, 'courses/section_list.html', context)

@login_required
@staff_required
def section_add(request, course_pk):
    """เพิ่ม Section ให้กับ Course ที่ระบุ"""
    course = get_object_or_404(Course, pk=course_pk)
    
    if request.method == 'POST':
        form = SectionForm(request.POST, course=course) 
        formset = ClassTimeFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            # บันทึก Section หลักก่อนเพื่อเอา pk
            section = form.save(commit=False)
            section.course = course
            section.save()
            
            # บันทึก M2M field (instructors)
            form.save_m2m()

            # เชื่อม formset กับ section ที่เพิ่งสร้าง
            formset.instance = section
            formset.save()    
            return redirect('courses:section-list', course_pk=course.pk)
    else:
        form = SectionForm(course=course)
        formset = ClassTimeFormSet()
        
    context = {
        'form': form,
        'formset': formset,
        'course': course
    }
    return render(request, 'courses/section_form.html', context)

@login_required
@staff_required
def section_edit(request, pk):
    """แก้ไข Section"""
    section = get_object_or_404(Section, pk=pk) # ดึง Section ที่ต้องการแก้ไข
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section, course=section.course) 
        formset = ClassTimeFormSet(request.POST, instance=section)
        if form.is_valid() and formset.is_valid():
            form.save()
            section.instructors.set(form.cleaned_data['instructors'])
            formset.save()
            return redirect('courses:section-list', course_pk=section.course.pk)
    else:
        form = SectionForm(instance=section, course=section.course)
        formset = ClassTimeFormSet(instance=section)
    
    context = {
        'form': form,
        'formset': formset,
        'course': section.course,
        'object': section
    }
    return render(request, 'courses/section_form.html', context)

@login_required
@staff_required
def section_delete(request, pk):
    """ลบ Section"""
    section = get_object_or_404(Section, pk=pk)
    course_pk_for_redirect = section.course.pk # เก็บ pk ของ course เพื่อ redirect หลังจากลบ
    if request.method == 'POST':
        section.delete()
        return redirect('courses:section-list', course_pk=course_pk_for_redirect)
    
    return render(request, 'courses/section_confirm_delete.html', {'object': section})

@login_required
def public_section_list(request):
    """หน้าสำหรับให้นิสิตดู Section ที่เปิดลงทะเบียน พร้อมฟังก์ชันค้นหา"""
    current_date = timezone.now().date()
    current_semester = Semester.objects.filter(start_date__lte=current_date, end_date__gte=current_date).first() # ดึงภาคเรียนปัจจุบัน

    
    sections_queryset = Section.objects.none() 

    if current_semester:
        # เริ่มต้น QuerySet ด้วยการกรองภาคเรียนปัจจุบันและสถานะของรายวิชา
        sections_queryset = Section.objects.filter(
            semester=current_semester,
            course__is_active=True
        )

        # ส่วนของการค้นหา
        query = request.GET.get('q') # ดึงคำค้นหาจากพารามิเตอร์ 'q' ใน URL
        if query: # ถ้ามีคำค้นหา
            # กรอง QuerySet เพิ่มเติมโดยใช้ Q object
            # ค้นหาในฟิลด์ course__code หรือ course__name แบบไม่สนใจตัวพิมพ์เล็ก-ใหญ่
            sections_queryset = sections_queryset.filter(
                Q(course__code__icontains=query) | # ค้นหาจากรหัสวิชา
                Q(course__name__icontains=query)   # ค้นหาจากชื่อวิชา
            )
        # --- สิ้นสุด Logic การค้นหา ---

        # เพิ่มการเลือกข้อมูลที่เกี่ยวข้องเพื่อเพิ่มประสิทธิภาพ
        sections_queryset = sections_queryset.select_related('course', 'room', 'semester').prefetch_related('instructors', 'students', 'class_times')
        
    context = {
        'sections': sections_queryset, # ส่ง QuerySet ที่ถูกกรองและ Optimize แล้วไปยัง Template
        'current_semester': current_semester,
    }
    return render(request, 'courses/public_section_list.html', context)

@login_required
@require_POST # บังคับให้ view นี้รับเฉพาะ POST request เพื่อความปลอดภัย
def enroll_section(request, section_pk):
    
    #จัดการการลงทะเบียน

    section = get_object_or_404(Section, pk=section_pk)
    student = request.user

    # ดึงรายวิชา (Course) ที่นักศึกษากำลังพยายามลงทะเบียน
    course_to_enroll = section.course
    # ค้นหากลุ่มเรียน (Sections) ทั้งหมดที่นักศึกษาลงทะเบียนไว้ในปัจจุบัน
    # และตรวจสอบว่ามีกลุ่มเรียนใดที่อยู่ในรายวิชาเดียวกันหรือไม่
    if student.enrolled_sections.filter(course=course_to_enroll).exists():
        messages.warning(request, f"คุณได้ลงทะเบียนวิชา {course_to_enroll.name} ไปแล้ว")
        return redirect('courses:public-section-list')

    # ตรวจสอบว่าเต็มหรือยัง
    if section.is_full():
        messages.error(request, f"ไม่สามารถลงทะเบียนได้: วิชา {section.course.name} (Sec {section.section_number}) เต็มแล้ว")
        return redirect('courses:public-section-list')

    # ตรวจสอบว่าลงทะเบียนไปแล้วหรือยัง (สำหรับกลุ่มเรียนนี้โดยเฉพาะ)
    if student in section.students.all():
        messages.warning(request, f"คุณได้ลงทะเบียนวิชา {section.course.name} (Sec {section.section_number}) ไปแล้ว")
        return redirect('courses:public-section-list')

    # ถ้าผ่านทุกเงื่อนไข ให้ทำการลงทะเบียน
    section.students.add(student)
    messages.success(request, f"ลงทะเบียนวิชา {section.course.name} (Sec {section.section_number}) สำเร็จ!")
    return redirect('courses:public-section-list')


@login_required
def my_schedule(request):
    """หน้าสำหรับดูตารางเรียนของฉัน"""
    current_date = timezone.now().date()
    current_semester = Semester.objects.filter(start_date__lte=current_date, end_date__gte=current_date).first() # ดึงภาคเรียนปัจจุบัน
    
    enrolled_sections = []
    if current_semester:
        enrolled_sections = request.user.enrolled_sections.filter(semester=current_semester) # ดึง Section ที่นิสิตลงทะเบียนในภาคเรียนปัจจุบัน

    context = {
        'enrolled_sections': enrolled_sections,
        'current_semester': current_semester,
    }
    return render(request, 'courses/my_schedule.html', context)