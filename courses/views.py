from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.db.models.deletion import ProtectedError
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from .models import (
    Branch,
    ClassTime,
    Course,
    Department,
    Faculty,
    Room,
    Section,
    Semester,
)
from .forms import (
    BranchForm,
    ClassTimeForm,
    CourseForm,
    DepartmentForm,
    FacultyForm,
    RoomForm,
    SectionForm,
    SemesterForm,
)
from payment.models import PaymentTransaction
from payment.payment_gateway import FakePaymentGateway
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

# เช็คว่าผู้ใช้เป็น staff ก่อนเข้าถึง view
def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


def student_required(view_func):
    """Allow access only to authenticated users with a student profile."""
    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if profile is None or profile.user_type != 'STUDENT':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


def get_current_semester():
    current_date = timezone.now().date()
    return Semester.objects.filter(
        start_date__lte=current_date,
        end_date__gte=current_date,
    ).order_by('start_date', 'pk').first()


MASTER_DATA_CONFIG = {
    'faculties': {
        'model': Faculty,
        'form_class': FacultyForm,
        'label': 'คณะ',
        'order_by': ('name',),
    },
    'departments': {
        'model': Department,
        'form_class': DepartmentForm,
        'label': 'ภาควิชา',
        'order_by': ('faculty__name', 'name'),
    },
    'branches': {
        'model': Branch,
        'form_class': BranchForm,
        'label': 'สาขาวิชา',
        'order_by': ('department__name', 'name'),
    },
    'rooms': {
        'model': Room,
        'form_class': RoomForm,
        'label': 'ห้องเรียน',
        'order_by': ('building', 'room_number'),
    },
    'semesters': {
        'model': Semester,
        'form_class': SemesterForm,
        'label': 'ภาคเรียน',
        'order_by': ('-year', 'semester'),
    },
}


def get_master_data_config(kind):
    try:
        return MASTER_DATA_CONFIG[kind]
    except KeyError as exc:
        raise Http404("ไม่พบประเภทข้อมูลตั้งต้น") from exc


@login_required
@staff_required
def master_data_index(request):
    items = [
        {
            'kind': kind,
            'label': config['label'],
            'count': config['model'].objects.count(),
        }
        for kind, config in MASTER_DATA_CONFIG.items()
    ]
    return render(request, 'courses/master_data_index.html', {'items': items})


@login_required
@staff_required
def master_data_list(request, kind):
    config = get_master_data_config(kind)
    objects = config['model'].objects.all().order_by(*config['order_by'])
    return render(request, 'courses/master_data_list.html', {
        'kind': kind,
        'label': config['label'],
        'objects': objects,
    })


@login_required
@staff_required
def master_data_form(request, kind, pk=None):
    config = get_master_data_config(kind)
    instance = None
    if pk is not None:
        instance = get_object_or_404(config['model'], pk=pk)

    form = config['form_class'](request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"บันทึก{config['label']}เรียบร้อยแล้ว")
        return redirect('courses:master-data-list', kind=kind)

    return render(request, 'courses/master_data_form.html', {
        'form': form,
        'kind': kind,
        'label': config['label'],
        'object': instance,
    })


@login_required
@staff_required
def master_data_delete(request, kind, pk):
    config = get_master_data_config(kind)
    instance = get_object_or_404(config['model'], pk=pk)

    if request.method == 'POST':
        try:
            instance.delete()
            messages.success(request, f"ลบ{config['label']}เรียบร้อยแล้ว")
        except ProtectedError:
            messages.error(
                request,
                f"ไม่สามารถลบ{config['label']}นี้ได้ เนื่องจากยังมีข้อมูลอื่นอ้างอิงอยู่"
            )
        return redirect('courses:master-data-list', kind=kind)

    return render(request, 'courses/master_data_confirm_delete.html', {
        'kind': kind,
        'label': config['label'],
        'object': instance,
    })

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
        
        if form.is_valid():
            # บันทึกข้อมูล
            section = form.save(commit=False)
            section.course = course
            section.save()
            section.instructors.set(form.cleaned_data['instructors'])

            return redirect('courses:section-list', course_pk=course.pk)
    else:
        form = SectionForm(course=course)
        
    context = {
        'form': form,
        'course': course,
        'object': None  # เพิ่มตรงนี้เพื่อให้ template รู้ว่าเป็นการเพิ่มใหม่
    }
    return render(request, 'courses/section_form.html', context)

@login_required
@staff_required
def section_edit(request, pk):
    """แก้ไข Section"""
    section = get_object_or_404(Section, pk=pk) # ดึง Section ที่ต้องการแก้ไข
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section, course=section.course) 
        if form.is_valid() :
            # บันทึกข้อมูล
            form.save()
            section.instructors.set(form.cleaned_data['instructors'])
            return redirect('courses:section-list', course_pk=section.course.pk)
    else:
        form = SectionForm(instance=section, course=section.course)
    
    context = {
        'form': form,
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
@student_required
def public_section_list(request):
    """หน้าสำหรับให้นิสิตดู Section ที่เปิดลงทะเบียน พร้อมฟังก์ชันค้นหา"""
    current_semester = get_current_semester()

    
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
@student_required
@require_POST # บังคับให้ view นี้รับเฉพาะ POST request เพื่อความปลอดภัย
def enroll_section(request, section_pk):
    student = request.user
    profile = student.profile

    # Lock the section row so concurrent requests cannot exceed its capacity.
    with transaction.atomic():
        section = get_object_or_404(
            Section.objects.select_for_update().select_related('course', 'semester'),
            pk=section_pk,
        )
        course_to_enroll = section.course
        current_semester = get_current_semester()

        if current_semester is None or section.semester_id != current_semester.pk:
            messages.error(request, "กลุ่มเรียนนี้ไม่ได้เปิดลงทะเบียนในภาคเรียนปัจจุบัน")
            return redirect('courses:public-section-list')

        if not course_to_enroll.is_active:
            messages.error(request, f"รายวิชา {course_to_enroll.name} ไม่ได้เปิดให้ลงทะเบียน")
            return redirect('courses:public-section-list')

        if section.students.count() >= section.capacity:
            messages.error(request, f"รายวิชา {course_to_enroll.name} (Sec {section.section_number}) เต็มแล้ว")
            return redirect('courses:public-section-list')

        # ตรวจสอบว่าลงทะเบียนไปแล้วหรือยัง
        if student.enrolled_sections.filter(
            course=course_to_enroll,
            semester=section.semester,
        ).exists():
            messages.warning(request, f"คุณได้ลงทะเบียนวิชา {course_to_enroll.name} ไปแล้ว")
            return redirect('courses:public-section-list')

        if course_to_enroll.fee > 0:
            if settings.PAYMENT_GATEWAY_MODE != 'fake':
                messages.error(
                    request,
                    "ระบบชำระเงินจริงยังไม่ได้เชื่อมต่อ จึงไม่สามารถลงทะเบียนวิชาที่มีค่าธรรมเนียมได้"
                )
                return redirect('courses:public-section-list')

            result = FakePaymentGateway.charge(student, course_to_enroll.fee)
            if not result["success"]:
                PaymentTransaction.objects.create(
                    student=profile,
                    course=course_to_enroll,
                    amount=course_to_enroll.fee,
                    status="FAILED"
                )
                messages.error(request, f"การชำระเงินสำหรับวิชา {course_to_enroll.name} ล้มเหลว")
                return redirect('courses:public-section-list')

            PaymentTransaction.objects.create(
                student=profile,
                course=course_to_enroll,
                amount=course_to_enroll.fee,
                status="SUCCESS",
                transaction_id=result["transaction_id"]
            )

        section.students.add(student)

    messages.success(request, f"ลงทะเบียนวิชา {section.course.name} (Sec {section.section_number}) สำเร็จ!")
    return redirect('courses:public-section-list')

@login_required
@staff_required
def time_list(request, section_pk):
    """แสดงรายการคาบเรียนของ Section"""
    section = get_object_or_404(Section, pk=section_pk)
    class_times = section.class_times.all().order_by('day', 'start_time')
    context = {
        'section': section,
        'class_times': class_times
    }
    return render(request, 'courses/time_list.html', context)

@login_required
@staff_required
def time_add(request, section_pk):
    """เพิ่มคาบเรียนให้กับ Section"""
    section = get_object_or_404(Section, pk=section_pk)
    
    if request.method == 'POST':
        form = ClassTimeForm(request.POST, section=section)
        if form.is_valid():
            class_time = form.save(commit=False)
            class_time.section = section
            class_time.save()
            messages.success(request, 'เพิ่มคาบเรียนสำเร็จ')
            return redirect('courses:time-list', section_pk=section.pk)
    else:
        form = ClassTimeForm()
    
    context = {
        'form': form,
        'section': section
    }
    return render(request, 'courses/time_form.html', context)

@login_required
@staff_required
def time_edit(request, pk):
    """แก้ไขคาบเรียน"""
    class_time = get_object_or_404(ClassTime, pk=pk)
    section = class_time.section
    
    if request.method == 'POST':
        form = ClassTimeForm(request.POST, instance=class_time, section=section)
        if form.is_valid():
            # ตรวจสอบการซ้ำซ้อนของเวลา (ไม่นับตัวเอง)
            if ClassTime.objects.filter(
                section=section,
                day=form.cleaned_data['day'],
                start_time__lt=form.cleaned_data['end_time'],
                end_time__gt=form.cleaned_data['start_time']
            ).exclude(pk=pk).exists():
                form.add_error(None, 'คาบเรียนนี้ซ้ำซ้อนกับคาบเรียนที่มีอยู่แล้ว')
            else:
                form.save()
                messages.success(request, 'แก้ไขคาบเรียนสำเร็จ')
                return redirect('courses:time-list', section_pk=section.pk)
    else:
        form = ClassTimeForm(instance=class_time)
    
    context = {
        'form': form,
        'section': section,
        'object': class_time
    }
    return render(request, 'courses/time_form.html', context)

@login_required
@staff_required
def time_delete(request, pk):
    """ลบคาบเรียน"""
    class_time = get_object_or_404(ClassTime, pk=pk)
    section = class_time.section
    
    if request.method == 'POST':
        class_time.delete()
        messages.success(request, 'ลบคาบเรียนสำเร็จ')
        return redirect('courses:time-list', section_pk=section.pk)
    
    context = {
        'object': class_time,
        'section': section
    }
    return render(request, 'courses/time_confirm_delete.html', context)

@login_required
@student_required
def my_schedule(request):
    """หน้าสำหรับดูตารางเรียนของฉัน"""
    current_semester = get_current_semester()
    
    enrolled_sections = []
    if current_semester:
        enrolled_sections = request.user.enrolled_sections.filter(semester=current_semester) # ดึง Section ที่นิสิตลงทะเบียนในภาคเรียนปัจจุบัน

    context = {
        'enrolled_sections': enrolled_sections,
        'current_semester': current_semester,
    }
    return render(request, 'courses/my_schedule.html', context)

@login_required
@student_required
def my_schedule_pdf(request):
    user = request.user
    current_semester = get_current_semester()

    enrolled_sections = []
    if current_semester:
        enrolled_sections = user.profile.get_schedule(current_semester)

    html = render_to_string('courses/my_schedule_pdf.html', {
        'user': user,
        'enrolled_sections': enrolled_sections,
        'current_semester': current_semester,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="schedule_{user.username}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f'เกิดข้อผิดพลาดในการสร้าง PDF <pre>{html}</pre>')

    return response
