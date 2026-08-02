# ระบบลงทะเบียนเรียน (Course Registration System)

เว็บแอปพลิเคชันสำหรับจัดการรายวิชา กลุ่มเรียน ตารางเรียน การลงทะเบียน และประวัติการชำระเงิน พัฒนาด้วย **Django 5.2** และ **PostgreSQL**

## สิ่งที่ต้องเตรียม

- Git
- Python 3.10 ขึ้นไป (แนะนำ Python 3.12 หรือ 3.13)
- PostgreSQL 14 ขึ้นไป และเครื่องมือ `psql`

ตรวจสอบเวอร์ชันได้ด้วยคำสั่ง:

```bash
python --version
psql --version
```

> บน Windows หาก `python` ใช้งานไม่ได้ ให้ใช้ `py` แทนในทุกคำสั่งด้านล่าง

## ติดตั้งและรันโปรเจกต์

### 1. ดาวน์โหลดโค้ด

```bash
git clone <repository-url>
cd course_registration_system-1
```

หากได้รับโฟลเดอร์โปรเจกต์มาอยู่แล้ว ให้เปิด Terminal/PowerShell ที่โฟลเดอร์นี้ได้เลย

### 2. สร้างและเปิดใช้ virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

หาก PowerShell แจ้งว่าไม่อนุญาตให้รันสคริปต์ ให้รันคำสั่งนี้หนึ่งครั้งในหน้าต่าง PowerShell เดิม แล้วสั่ง activate อีกครั้ง:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. ติดตั้ง Python packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. สร้างฐานข้อมูล PostgreSQL

เข้าสู่ PostgreSQL ด้วยผู้ใช้ที่มีสิทธิ์สร้างฐานข้อมูล แล้วสร้างฐานข้อมูลและผู้ใช้สำหรับโปรเจกต์:

```sql
CREATE USER course_registration_user WITH PASSWORD 'ตั้งรหัสผ่านที่คาดเดายาก';
CREATE DATABASE course_registration_system OWNER course_registration_user;
```

### 5. ตั้งค่าตัวแปรแวดล้อม

คัดลอกไฟล์ตัวอย่างเป็น `.env`:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

จากนั้นแก้ไขไฟล์ `.env` ให้ตรงกับฐานข้อมูลของเครื่อง เช่น:

```env
SECRET_KEY=replace-with-a-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
PAYMENT_GATEWAY_MODE=disabled

NAME_DB=course_registration_system
USER_DB=course_registration_user
PASSWORD_DB=ตั้งรหัสผ่านเดียวกับที่สร้างใน PostgreSQL
HOST_DB=localhost
PORT_DB=5432
```

สามารถสร้างค่า `SECRET_KEY` ใหม่ได้ด้วย:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

อย่าส่งไฟล์ `.env` ขึ้น Git หรือเผยแพร่รหัสผ่านและ `SECRET_KEY`

### 6. สร้างตารางในฐานข้อมูล

```bash
python manage.py migrate
```

### 7. สร้างข้อมูลสาธิต (แนะนำสำหรับการเรียนรู้)

```bash
python manage.py seed_mock_data
```

คำสั่งนี้สร้างคณะ ภาควิชา สาขา รายวิชา กลุ่มเรียน ตารางเรียน ผู้ใช้ และรายการชำระเงินตัวอย่าง โดยรันซ้ำได้อย่างปลอดภัย

### 8. เริ่มเซิร์ฟเวอร์

```bash
python manage.py runserver
```

เปิดเบราว์เซอร์ที่ [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## บัญชีสาธิต

หลังจากรัน `seed_mock_data` ทุกบัญชีใช้รหัสผ่านเดียวกันคือ `DemoPass123!`

| บทบาท | Username | หน้าที่ที่ลองใช้งาน |
| --- | --- | --- |
| เจ้าหน้าที่ | `registrar` | จัดการรายวิชา กลุ่มเรียน และข้อมูลหลัก |
| อาจารย์ | `somchai` | ดูระบบในบทบาทอาจารย์ |
| อาจารย์ | `suda` | ดูระบบในบทบาทอาจารย์ |
| นักศึกษา | `student_66000001` | ลงทะเบียนและดูตารางเรียน |
| นักศึกษา | `student_66000002` | ลงทะเบียนและดูตารางเรียน |
| นักศึกษา | `student_66000003` | ลงทะเบียนและดูตารางเรียน |
| นักศึกษา | `student_66000004` | ลงทะเบียนและดูตารางเรียน |

หน้าเข้าสู่ระบบอยู่ที่ [http://127.0.0.1:8000/users/login/](http://127.0.0.1:8000/users/login/)

## URL สำคัญ

| URL | รายละเอียด |
| --- | --- |
| `/` | หน้าหลัก |
| `/manage/courses/` | จัดการรายวิชาและกลุ่มเรียน |
| `/manage/courses/master-data/` | จัดการข้อมูลหลัก เช่น คณะ ภาควิชา ห้องเรียน ภาคการศึกษา |
| `/manage/courses/register/` | หน้าลงทะเบียนเรียน |
| `/manage/courses/my-schedule/` | ตารางเรียนของผู้ใช้ที่เข้าสู่ระบบ |
| `/users/students/` | รายชื่อนักศึกษา |
| `/users/payment-history/` | ประวัติการชำระเงิน |
| `/admin/` | Django Admin |

## การชำระเงินในเครื่องพัฒนา

ค่าเริ่มต้น `PAYMENT_GATEWAY_MODE=disabled` จะไม่เรียกบริการชำระเงินจริง สำหรับการสาธิต flow การชำระเงินสามารถตั้งค่าเป็น:

```env
PAYMENT_GATEWAY_MODE=fake
```

โหมด `fake` มีไว้สำหรับการพัฒนาและการทดสอบเท่านั้น ห้ามนำไปใช้กับระบบจริง

## รันชุดทดสอบ

ก่อนรันทดสอบ ต้องตั้งค่า `.env` และให้ PostgreSQL ทำงานอยู่:

```bash
pytest
```

หรือทดสอบเฉพาะแอป:

```bash
pytest courses/tests
```

## คำสั่งที่ใช้บ่อย

```bash
# สร้างผู้ดูแลระบบ Django Admin
python manage.py createsuperuser

# ตรวจสอบปัญหาการตั้งค่า Django
python manage.py check

# สร้าง migration เมื่อมีการแก้ไข model
python manage.py makemigrations

# นำ migration ไปใช้กับฐานข้อมูล
python manage.py migrate
```

## แก้ปัญหาเบื้องต้น

**เชื่อมต่อ PostgreSQL ไม่ได้**  
ตรวจสอบว่า PostgreSQL service ทำงานอยู่ และค่า `NAME_DB`, `USER_DB`, `PASSWORD_DB`, `HOST_DB`, `PORT_DB` ใน `.env` ถูกต้อง

**พบ `ModuleNotFoundError`**  
ตรวจสอบว่าเปิดใช้ virtual environment แล้ว และรัน `pip install -r requirements.txt` สำเร็จ

**พบ `SECRET_KEY` หรือ environment variable error**  
ตรวจสอบว่ามีไฟล์ `.env` อยู่ที่โฟลเดอร์เดียวกับ `manage.py` และกำหนดค่าครบตาม `.env.example`

**พอร์ต 8000 ถูกใช้งานอยู่**  
รันบนพอร์ตอื่น เช่น:

```bash
python manage.py runserver 8001
```

## โครงสร้างโปรเจกต์

```text
course_registration_system/  # การตั้งค่า Django และ URL หลัก
core/                        # หน้าหลักและส่วนประกอบร่วม
courses/                     # รายวิชา กลุ่มเรียน ตารางเรียน และการลงทะเบียน
users/                       # ผู้ใช้ นักศึกษา และการเข้าสู่ระบบ
payment/                     # รายการและกระบวนการชำระเงิน
Doc/                         # เอกสารประกอบโครงการ
```

## หมายเหตุสำหรับการนำขึ้นใช้งานจริง

คู่มือนี้มุ่งสำหรับการรันในเครื่องเพื่อการเรียนรู้เท่านั้น ก่อน deploy จริง ให้ตั้ง `DEBUG=False`, ใช้ `SECRET_KEY` ที่ปลอดภัย, จำกัด `ALLOWED_HOSTS`, เก็บรหัสผ่านใน secret manager และตั้งค่าฐานข้อมูล/การชำระเงินสำหรับสภาพแวดล้อม production โดยเฉพาะ
