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
        fields = ['code', 'name', 'department', 'credits', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'เช่น 012457'
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
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'credits': 'จำนวนหน่วยกิต 1-9 หน่วยกิต',
            'is_active': 'เปิด/ปิด การใช้งานรายวิชา'
        }
        error_messages = {
            'code': {
                'required': 'กรุณากรอกรหัสวิชา',
                'unique': 'รหัสวิชานี้มีอยู่ในระบบแล้ว',
            },
            'name': {'required': 'กรุณากรอกชื่อวิชา'},
            'department': {'required': 'กรุณาเลือกภาควิชา'},
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
            'class': 'form-control select2',
            'data-placeholder': 'เลือกอาจารย์ผู้สอน'
        }),
        required=True,
        label="อาจารย์ผู้สอน",
        help_text="เลือกอาจารย์ผู้สอน"
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.all().order_by('building', 'room_number'),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-placeholder': 'เลือกห้องเรียน'
        }),
        required=True,
        label="ห้องเรียน",
        help_text="เลือกห้องเรียนที่ใช้สอน"
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
                'min': '1',
                'max': '200',
                'placeholder': 'จำนวนที่รับ'
            })
        }
        help_texts = {
            'semester': 'เลือกภาคการศึกษา',
            'section_number': 'กรอกหมายเลขกลุ่มเรียน (1-99)',
            'capacity': 'ระบุจำนวนที่รับนิสิต (1-200 คน)',
        }
        error_messages = {
            'semester': {'required': 'กรุณาเลือกภาคการศึกษา'},
            'section_number': {'required': 'กรุณากรอกหมายเลขกลุ่มเรียน'},
            'room': {'required': 'กรุณาเลือกห้องเรียน'},
            'capacity': {
                'required': 'กรุณากรอกจำนวนที่รับ',
                'min_value': 'จำนวนที่รับต้องไม่น้อยกว่า 1 คน',
                'max_value': 'จำนวนที่รับต้องไม่เกิน 200 คน',
            },
            'instructors': {'required': 'กรุณาเลือกอาจารย์ผู้สอนอย่างน้อย 1 คน'},
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({'class': 'form-control'})

# Form สำหรับ ClassTime
class ClassTimeForm(forms.ModelForm):
    class Meta:
        model = ClassTime
        fields = ['day', 'start_time', 'end_time']
        widgets = {
            'day': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'เลือกวัน'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
        }
        help_texts = {
            'day': 'เลือกวันที่เรียน',
            'start_time': 'เวลาเริ่มเรียน (08:00-20:00)',
            'end_time': 'เวลาเลิกเรียน (09:00-21:00)',
        }
        error_messages = {
            'day': {'required': 'กรุณาเลือกวัน'},
            'start_time': {'required': 'กรุณากรอกเวลาเริ่ม'},
            'end_time': {'required': 'กรุณากรอกเวลาเลิก'},
        }
        
    def clean(self):
        """
        ตรวจสอบว่าถ้ากรอกข้อมูลในแถวแล้ว ต้องกรอกให้ครบทุกช่อง
        """
        cleaned_data = super().clean()
        
        # ดึงข้อมูลจากฟอร์ม
        day = cleaned_data.get('day')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # ตรวจสอบว่าฟอร์มนี้ไม่ใช่ฟอร์มเปล่าที่ไม่ได้กรอกอะไรเลย
        # และไม่ได้ถูกติ๊กเพื่อลบ
        is_empty = not any([day, start_time, end_time])
        is_marked_for_deletion = cleaned_data.get('DELETE', False)

        if not is_empty and not is_marked_for_deletion:
            # ถ้ามีข้อมูลอย่างน้อย 1 ช่อง แต่ไม่ครบทุกช่อง
            if not all([day, start_time, end_time]):
                # เพิ่ม Error ให้กับฟิลด์ที่ว่าง
                if not day:
                    self.add_error('day', 'กรุณาเลือกวัน')
                if not start_time:
                    self.add_error('start_time', 'กรุณากรอกเวลาเริ่ม')
                if not end_time:
                    self.add_error('end_time', 'กรุณากรอกเวลาเลิก')
            
            # (Optional) ตรวจสอบว่าเวลาเลิกเรียนอยู่หลังเวลาเริ่มเรียน
            elif end_time <= start_time:
                self.add_error('end_time', 'เวลาเลิกเรียนต้องอยู่หลังเวลาเริ่มเรียน')
        
        return cleaned_data
    
class BaseClassTimeFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                count += 1
        
        if count < 1:
            raise forms.ValidationError('กรุณากรอกข้อมูลคาบเรียนอย่างน้อย 1 คาบเรียน')

# Formset สำหรับ ClassTime
# สร้าง ClassTimeFormSet โดยใช้ inlineformset_factory
# Inline Formset ใช้จัดการข้อมูลที่เกี่ยวข้อง (related objects) ของโมเดลหลัก
ClassTimeFormSet = inlineformset_factory(
    Section, # โมเดลหลัก (Parent Model): ClassTime จะถูกเชื่อมโยงกับ Section
    ClassTime, # โมเดลลูก (Child Model): ClassTime คือข้อมูลที่จะถูกจัดการผ่าน Formset นี้
    form=ClassTimeForm, # ใช้ ClassTimeForm ที่เราสร้างไว้ก่อนหน้านี้สำหรับแต่ละฟอร์มใน Formset
    formset=BaseClassTimeFormSet, # ใช้ BaseClassTimeFormSet ที่เราสร้างไว้เพื่อจัดการการตรวจสอบความถูกต้อง
    extra=1, # จำนวนฟอร์มเปล่าเพิ่มเติมที่จะแสดงในหน้า (สำหรับเพิ่มรายการใหม่)
             # ในที่นี้คือจะแสดงฟอร์มเปล่า 1 ฟอร์มเสมอ
    can_delete=True, # อนุญาตให้ผู้ใช้สามารถลบรายการ ClassTime ที่มีอยู่ได้
                     # จะมี checkbox "Delete" ปรากฏขึ้นข้างๆ แต่ละรายการ
    can_delete_extra=True, # อนุญาตให้ผู้ใช้ลบฟอร์มเปล่าที่ถูกเพิ่มโดย 'extra'
                          # (ถ้าผู้ใช้เพิ่มฟอร์มเปล่าขึ้นมาแล้วตัดสินใจไม่ใช้ ก็สามารถลบได้)
)