from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.contrib.auth.models import User
from .models import Course, Section, ClassTime, Room

# Form Field สำหรับเลือกอาจารย์
class InstructorChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if hasattr(obj, 'profile') and obj.profile.first_name_th and obj.profile.last_name_th:
            # ใช้ get_acdemic_title_display() เพื่อดึงค่าภาษาไทย
            title = obj.profile.get_acdemic_title_display() or ''
            first_name = obj.profile.first_name_th
            last_name = obj.profile.last_name_th
            return f"{title} {first_name} {last_name}".strip()
        return obj.username

# Form สำหรับ Course
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'credits', 'department', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'เช่น 012345'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อวิชา'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'credits': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 9
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'อธิบายรายละเอียดของรายวิชา'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'}),
        }
        help_texts = {
            'department': 'เลือกภาควิชาที่สอนรายวิชานี้',
            'credits': 'จำนวนหน่วยกิต 1-9 หน่วยกิต',
            'is_active': 'เปิด/ปิด การใช้งานรายวิชา'
        }
        error_messages = {
            'code': {
                'required': 'กรุณากรอกรหัสวิชา',
                'unique': 'รหัสวิชานี้มีอยู่ในระบบแล้ว',
            },
            'name': {'required': 'กรุณากรอกชื่อวิชา'},
            'credits': {
                'required': 'กรุณากรอกจำนวนหน่วยกิต',
                'min_value': 'หน่วยกิตต้องไม่น้อยกว่า 1',
                'max_value': 'หน่วยกิตต้องไม่เกิน 9',
            },
        }

    def __init__(self, *args, **kwargs):
        """
        ปรับแต่งการเริ่มต้นของฟอร์ม

        เพิ่มคลาส CSS 'form-control' ให้กับ widget ทุกตัว
        ยกเว้น CheckboxInput เพื่อให้สอดคล้องกับ Bootstrap
        """
        super().__init__(*args, **kwargs) # เรียกใช้ constructor ของคลาสแม่ (ModelForm)
        
        # วนลูปผ่านทุกฟิลด์ในฟอร์ม
        for field_name, field in self.fields.items():
            # ตรวจสอบว่า widget ของฟิลด์นั้นไม่ใช่ CheckboxInput
            # (เนื่องจาก CheckboxInput ไม่ต้องการคลาส form-control)
            if not isinstance(field.widget, forms.CheckboxInput):
                # เพิ่มคลาส 'form-control' ให้กับ attribute ของ widget
                # ซึ่งจะช่วยให้ฟอร์มแสดงผลได้สวยงามตามสไตล์ Bootstrap
                field.widget.attrs.update({'class': 'form-control'})

# Form สำหรับ Section
class SectionForm(forms.ModelForm):
    instructors = InstructorChoiceField(
        queryset=User.objects.filter(profile__user_type='INSTRUCTOR'),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2',
            'data-placeholder': 'เลือกอาจารย์ผู้สอน'
        }),
        required=True,
        label="อาจารย์ผู้สอน",
        help_text="เลือกอาจารย์ผู้สอนที่รับผิดชอบการสอนในกลุ่มเรียนนี้",
        error_messages={
            'required': 'กรุณาเลือกอาจารย์ผู้สอนอย่างน้อย 1 คน'
        }
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.all().order_by('building', 'room_number'),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-placeholder': 'เลือกห้องเรียน'
        }),
        required=True,
        label="ห้องเรียน",
        help_text="เลือกห้องเรียนที่ใช้จัดการเรียนการสอน",
        error_messages={
            'required': 'กรุณาเลือกห้องเรียนอย่างน้อย 1 ห้อง'
        }
    )
    class Meta:
        model = Section
        fields = ['semester', 'section_number', 'room', 'capacity', 'instructors']
        widgets = {
            'semester': forms.Select(attrs={
                'class': 'form-select'
            }),
            'section_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'เช่น 1, 2, 3'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'จำนวนที่รับ (1-200)'
            })
        }
        help_texts = {
            'semester': 'เลือกภาคการศึกษาที่เปิดสอนรายวิชานี้',
            'section_number': 'กำหนดหมายเลขกลุ่มเรียน (1-99) สำหรับแยกกลุ่มเรียนในรายวิชา',
            'capacity': 'กำหนดจำนวนนักศึกษาที่รับเข้าในกลุ่มเรียนนี้ (1-200 คน)',
        }
        error_messages = {
            'semester': {'required': 'กรุณาเลือกภาคการศึกษา'},
            'section_number': {'required': 'กรุณากรอกหมายเลขกลุ่มเรียน',},
            'room': {'required': 'กรุณาเลือกห้องเรียน'},
            'capacity': {
                'required': 'กรุณากรอกจำนวนที่รับ',
                'min_value': 'จำนวนที่รับต้องไม่น้อยกว่า 1 คน',
                'max_value': 'จำนวนที่รับต้องไม่เกิน 200 คน',
            },
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({'class': 'form-control'})
                
    def clean(self):
        cleaned_data = super().clean()
        section_number = cleaned_data.get('section_number')
        semester = cleaned_data.get('semester')
        
        
        if section_number and semester and self.course:
            # สร้าง query เพื่อตรวจสอบการซ้ำซ้อน
            qs = Section.objects.filter(
                course=self.course,
                semester=semester,
                section_number=section_number
            )
            
            # ถ้าเป็นการแก้ไข ไม่นับตัวเองในการตรวจสอบ
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            # ถ้ามีการซ้ำ ให้เพิ่ม error
            if qs.exists():
                self.add_error(
                    'section_number',
                    'กลุ่มเรียน (Sec) หมายเลขนี้มีอยู่แล้วในรายวิชาและภาคเรียนเดียวกัน'
                )
        
        return cleaned_data
    
# Form สำหรับคาบเรียน
class ClassTimeForm(forms.ModelForm):
    class Meta:
        model = ClassTime
        fields = ['day', 'start_time', 'end_time']
        widgets = {
            'day': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'เลือกวัน'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            })
        }
        help_texts = {
            'day': 'เลือกวันที่จัดการเรียนการสอน',
            'start_time': 'เวลาเริ่มต้นคาบเรียน (เช่น 09:00)',
            'end_time': 'เวลาสิ้นสุดคาบเรียน (เช่น 12:00)'
        }
        error_messages = {
            'day': {'required': 'กรุณาเลือกวัน'},
            'start_time': {'required': 'กรุณาระบุเวลาเริ่มต้น'},
            'end_time': {'required': 'กรุณาระบุเวลาสิ้นสุด'}
        }
