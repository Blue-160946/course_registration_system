from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.views import staff_required
from .models import User

def staff_login_view(request):
    if request.user.is_authenticated:
        return redirect('core:index') # ถ้าล็อกอินอยู่แล้ว ให้ไปหน้าแรก

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            # ตรวจสอบว่า authenticate สำเร็จ และ user เป็น staff
            # ตรวจสอบก่อนว่า authenticate สำเร็จหรือไม่
            if user is not None:
                # ตรวจสอบสิทธิ์และล็อกอิน
                if user.is_staff:
                    login(request, user)
                    # ส่งไปหน้าจัดการสำหรับเจ้าหน้าที่
                    return redirect('courses:course-list')
                    
                elif hasattr(user, 'profile') and user.profile.user_type == 'STUDENT':
                    login(request, user)
                    # ส่งไปหน้าลงทะเบียนเรียนสำหรับนิสิต
                    return redirect('courses:public-section-list')
                    
                else:
                    # กรณีเป็น User ประเภทอื่นที่ไม่มีสิทธิ์เข้าใช้งาน
                    messages.error(request, "คุณไม่มีสิทธิ์เข้าใช้งานในส่วนนี้")

            else:
                # กรณี authenticate ไม่สำเร็จ (username/password ผิด)
                messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
@staff_required
def student_list(request):
    """แสดงรายการนิสิตทั้งหมด"""
    students = User.objects.filter(profile__user_type='STUDENT').select_related('profile', 'profile__branch') # ใช้ select_related เพื่อเพิ่มประสิทธิภาพการดึงข้อมูล
    return render(request, 'users/student_list.html', {'students': students})

@login_required
@staff_required
def student_detail(request, pk):
    """แสดงรายละเอียดของนิสิต 1 คน"""
    student = get_object_or_404(User, pk=pk, profile__user_type='STUDENT')
    return render(request, 'users/student_detail.html', {'student': student})