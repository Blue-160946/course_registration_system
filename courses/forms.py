from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from .models import Course, Section, ClassTime, Room

# Form Field สำหรับเลือกอาจารย์
class InstructorChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if hasattr(obj, 'profile') and obj.profile.instructor_name:
            return obj.profile.instructor_name
        return obj.username

# Form สำหรับ Course
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'department', 'credits', 'description', 'is_active']
        widgets = { 'description': forms.Textarea(attrs={'rows': 4}), }
    
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
        widget=forms.SelectMultiple, # Widget สำหรับ Select2
        required=True,
        label="อาจารย์ผู้สอน"
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="ห้องเรียน"
    )
    class Meta:
        model = Section
        fields = ['semester', 'section_number', 'room', 'capacity', 'instructors']

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        """
        เมธอด clean() สำหรับการตรวจสอบความถูกต้องของข้อมูลแบบกำหนดเอง

        รับประกันว่าหมายเลขกลุ่มเรียน (section number) จะต้องไม่ซ้ำกัน
        สำหรับรายวิชาและภาคเรียนเดียวกัน เพื่อป้องกันการบันทึกข้อมูลซ้ำซ้อน
        """
        # เรียกใช้เมธอด clean ของคลาสแม่ก่อน เพื่อให้มีการตรวจสอบเบื้องต้นของฟิลด์ต่างๆ
        cleaned_data = super().clean()

        # ดึงข้อมูลจากฟิลด์ที่ผ่านการตรวจสอบเบื้องต้นแล้ว
        section_number = cleaned_data.get("section_number")
        semester = cleaned_data.get("semester")

        # ดำเนินการตรวจสอบความไม่ซ้ำกันเฉพาะเมื่อมีข้อมูลที่จำเป็นครบถ้วน
        if section_number and semester and self.course:
            # สร้าง QuerySet เพื่อค้นหากลุ่มเรียนที่มี course, semester และ section_number เดียวกัน
            queryset = Section.objects.filter(
                course=self.course,
                semester=semester,
                section_number=section_number
            )

            # หากกำลังแก้ไข instance ที่มีอยู่ (ไม่ใช่การสร้างใหม่)
            # ให้ยกเว้น instance ปัจจุบันออกจาก QuerySet
            # เพื่อไม่ให้ฟอร์มตรวจสอบตัวเองว่าซ้ำกัน
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            # หากยังพบกลุ่มเรียนที่ตรงกันใน QuerySet (หลังจากยกเว้น instance ปัจจุบันแล้ว)
            # แสดงว่ามีการซ้ำกัน
            if queryset.exists():
                # ยิง ValidationError เพื่อแจ้งให้ผู้ใช้ทราบถึงข้อผิดพลาด
                raise forms.ValidationError(
                    "กลุ่มเรียน (Sec) หมายเลขนี้มีอยู่แล้วในรายวิชาและภาคเรียนเดียวกัน"
                )
        # คืนค่า cleaned_data ไม่ว่าจะมีข้อผิดพลาดหรือไม่ (ข้อผิดพลาดจะถูกเก็บใน form.errors)
        return cleaned_data

# Form สำหรับ ClassTime
class ClassTimeForm(forms.ModelForm):
    class Meta:
        model = ClassTime
        fields = ['day', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'day': forms.Select(attrs={'class': 'form-select'}),
        }

# Formset สำหรับ ClassTime
# สร้าง ClassTimeFormSet โดยใช้ inlineformset_factory
# Inline Formset ใช้จัดการข้อมูลที่เกี่ยวข้อง (related objects) ของโมเดลหลัก
ClassTimeFormSet = inlineformset_factory(
    Section, # โมเดลหลัก (Parent Model): ClassTime จะถูกเชื่อมโยงกับ Section
    ClassTime, # โมเดลลูก (Child Model): ClassTime คือข้อมูลที่จะถูกจัดการผ่าน Formset นี้
    form=ClassTimeForm, # ใช้ ClassTimeForm ที่เราสร้างไว้ก่อนหน้านี้สำหรับแต่ละฟอร์มใน Formset
    extra=1, # จำนวนฟอร์มเปล่าเพิ่มเติมที่จะแสดงในหน้า (สำหรับเพิ่มรายการใหม่)
             # ในที่นี้คือจะแสดงฟอร์มเปล่า 1 ฟอร์มเสมอ
    can_delete=True, # อนุญาตให้ผู้ใช้สามารถลบรายการ ClassTime ที่มีอยู่ได้
                     # จะมี checkbox "Delete" ปรากฏขึ้นข้างๆ แต่ละรายการ
    can_delete_extra=True # อนุญาตให้ผู้ใช้ลบฟอร์มเปล่าที่ถูกเพิ่มโดย 'extra'
                          # (ถ้าผู้ใช้เพิ่มฟอร์มเปล่าขึ้นมาแล้วตัดสินใจไม่ใช้ ก็สามารถลบได้)
)