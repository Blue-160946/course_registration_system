*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/login.robot
Resource    ../resource/addsubject.robot
Resource    ../resource/editsubject.robot
Test Teardown    Close All Browsers

*** Test Cases ***
TC01 Admin Can Edit Subject Successfully
    [Documentation]    ผู้ดูแลระบบสามารถแก้ไขรายวิชาและเห็นข้อมูลใหม่ในรายการ
    [Tags]    editsubject    positive
    Open Manage Courses Page As Admin
    ${original_code}=    Generate Random String    6    [NUMBERS]
    ${original_name}=    Set Variable    วิชาเดิม ${original_code}
    Add Subject With Custom Data    ${original_code}    ${original_name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    วิชาสำหรับทดสอบการแก้ไข
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${original_code}']    10s
    Open Subject Edit Form By Course Code    ${original_code}
    ${new_code}=    Generate Random String    6    [NUMBERS]
    ${new_name}=    Set Variable    วิชาแก้ไข ${new_code}
    Fill Subject Edit Form    ${new_code}    ${new_name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    4    วิชาที่ผ่านการแก้ไข
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${new_code}']    10s
    Element Should Contain    xpath=//tr[td[normalize-space()='${new_code}']]/td[2]    ${new_name}

TC02 Edit Subject With Invalid Code Should Show Validation
    [Documentation]    ระบบต้องแสดงข้อความแจ้งเตือนเมื่อแก้ไขรหัสวิชาเป็นรูปแบบที่ไม่ถูกต้อง
    [Tags]    editsubject    negative    validation
    Open Manage Courses Page As Admin
    ${code}=    Generate Random String    6    [NUMBERS]
    ${name}=    Set Variable    วิชาทดสอบโค้ดไม่ถูกต้อง ${code}
    Add Subject With Custom Data    ${code}    ${name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    ใช้สำหรับทดสอบรหัสผิดรูปแบบ
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${code}']    10s
    Open Subject Edit Form By Course Code    ${code}
    Fill Subject Edit Form    ABC123    ${name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    รหัสไม่ตรงรูปแบบ
    Wait Until Location Contains    /edit/    10s
    Wait Until Page Contains    รหัสวิชาต้องเป็นตัวเลข 6 หลัก    10s
    Click Cancel Edit Form
    Wait Until Location Contains    /manage/courses/    10s

TC03 Edit Subject Without Name Should Show Validation
    [Documentation]    ระบบต้องแจ้งเตือนเมื่อแก้ไขแล้วไม่กรอกชื่อวิชา
    [Tags]    editsubject    negative    validation
    Open Manage Courses Page As Admin
    ${code}=    Generate Random String    6    [NUMBERS]
    ${name}=    Set Variable    วิชาทดสอบไม่มีชื่อ ${code}
    Add Subject With Custom Data    ${code}    ${name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    ใช้สำหรับทดสอบเว้นชื่อว่าง
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${code}']    10s
    Open Subject Edit Form By Course Code    ${code}
    ${new_code}=    Generate Random String    6    [NUMBERS]
    Fill Subject Edit Form    ${new_code}    ${EMPTY}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    ปล่อยชื่อว่าง
    Wait Until Location Contains    /edit/    10s
    Wait Until Page Contains    กรุณากรอกชื่อวิชา    10s
    Click Cancel Edit Form
    Wait Until Location Contains    /manage/courses/    10s

*** Keywords ***
Open Manage Courses Page As Admin
    Open browser
    Login    admin    12345678
    Should See Manage Courses Dashboard

Click Cancel Edit Form
    Click Element    xpath=//a[contains(@class, 'btn-secondary') and contains(., 'ยกเลิก')]
