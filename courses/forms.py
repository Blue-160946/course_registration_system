from datetime import date, datetime
from django import forms
from django.forms import BaseInlineFormSet, ValidationError, inlineformset_factory
from django.contrib.auth.models import User
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


class MasterDataModelForm(forms.ModelForm):
    """Shared Bootstrap styling for staff-managed master data forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'
            field.widget.attrs.update({'class': css_class})


class FacultyForm(MasterDataModelForm):
    class Meta:
        model = Faculty
        fields = ['name']


class DepartmentForm(MasterDataModelForm):
    class Meta:
        model = Department
        fields = ['name', 'faculty']


class BranchForm(MasterDataModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'department']


class RoomForm(MasterDataModelForm):
    class Meta:
        model = Room
        fields = ['building', 'room_number']


class SemesterForm(MasterDataModelForm):
    class Meta:
        model = Semester
        fields = ['year', 'semester', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

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
        fields = ['code', 'name', 'credits', 'department', 'fee','description', 'is_active']
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
            'fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'ค่าธรรมเนียม'
            }),
        }
        help_texts = {
            'department': 'เลือกภาควิชาที่สอนรายวิชานี้',
            'credits': 'จำนวนหน่วยกิต 1-9 หน่วยกิต',
            'is_active': 'เปิด/ปิด การใช้งานรายวิชา',
            'fee': 'กรุณากรอกค่าธรรมเนียมสำหรับรายวิชา'
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
        room = cleaned_data.get('room')
        
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
        
    def __init__(self, *args, **kwargs):
        self.section = kwargs.pop('section', None)  # รับ Section ที่เกี่ยวข้อง
        super().__init__(*args, **kwargs)
        
    def clean(self):
        """
        ตรวจสอบความถูกต้องของเวลาการสอนใน Form
        - end_time ต้องอยู่หลัง start_time
        - ระยะเวลาเรียนไม่เกิน 2 ชั่วโมง
        - ตรวจสอบการชนกันของเวลาใน Section, Room และ Instructor
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        day = cleaned_data.get('day')

        # ถ้าไม่มีข้อมูลเพียงพอ ให้ข้าม validation
        if not start_time or not end_time or not day or not self.section:
            return cleaned_data

        errors = {}

        # 1. ตรวจสอบว่า end_time หลัง start_time
        if end_time <= start_time:
            errors['end_time'] = 'เวลาเลิกเรียนต้องอยู่หลังเวลาเริ่มเรียน'

        # 2. ตรวจสอบระยะเวลาไม่เกิน 2 ชั่วโมง
        duration = (datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)).seconds / 3600
        if duration > 2:
            errors['__all__'] = errors.get('__all__', []) + ['ระยะเวลาเรียนต้องไม่เกิน 2 ชั่วโมงต่อคาบ']

        # 3. ตรวจสอบเวลาชนกันเฉพาะเมื่อใช้ Section/Room/Instructor ร่วมกัน
        possible_conflicts = ClassTime.objects.filter(
            section__semester=self.section.semester,
            day=day
        ).exclude(id=self.instance.id if self.instance else None)

        instructor_ids = set(self.section.instructors.values_list('id', flat=True))

        for time in possible_conflicts:
            start_existing = time.start_time
            end_existing = time.end_time

            # รักษากติกาเดิม: คาบที่ชนขอบกันถือว่าใช้ทรัพยากรชนกันด้วย
            if start_time > end_existing or end_time < start_existing:
                continue

            if time.section_id == self.section.id:
                if start_time == end_existing or end_time == start_existing:
                    errors['__all__'] = errors.get('__all__', []) + [
                        f'เวลาชนขอบกัน: คาบเรียน {start_time}-{end_time} ติดกับคาบ '
                        f'{start_existing}-{end_existing} ในกลุ่มเรียนเดียวกัน'
                    ]
                    continue

                errors['__all__'] = errors.get('__all__', []) + [
                    f'คาบเรียน {start_time}-{end_time} ชนกับคาบ {start_existing}-{end_existing} '
                    f'ในกลุ่มเรียนเดียวกัน'
                ]
                continue

            if self.section.room_id and self.section.room_id == time.section.room_id:
                errors['__all__'] = errors.get('__all__', []) + [
                    f'เวลาซ้อนทับกัน: ห้อง {self.section.room} ทับกับวิชา '
                    f'{time.section.course.name} กลุ่ม {time.section.section_number} '
                    f'ช่วงเวลา {start_existing}-{end_existing}'
                ]
                continue

            conflicting_ids = instructor_ids.intersection(
                time.section.instructors.values_list('id', flat=True)
            )
            if conflicting_ids:
                conflicting_instructors = self.section.instructors.filter(id__in=conflicting_ids)
                names = ", ".join(
                    instructor.get_full_name() or instructor.username
                    for instructor in conflicting_instructors
                )
                errors['__all__'] = errors.get('__all__', []) + [
                    f'อาจารย์ ({names}) มีตารางสอนชนกันกับวิชา {time.section.course.name} '
                    f'กลุ่ม {time.section.section_number} ช่วงเวลา {start_existing}-{end_existing}'
                ]

        # 4. เพิ่ม error ทั้งหมด
        for field, messages in errors.items():
            if field == '__all__':
                for message in messages:
                    self.add_error(None, message)
            else:
                for message in messages if isinstance(messages, list) else [messages]:
                    self.add_error(field, message)

        return cleaned_data
