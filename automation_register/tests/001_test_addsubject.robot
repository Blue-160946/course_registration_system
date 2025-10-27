*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/login.robot
Resource    ../resource/addsubject.robot
Test Teardown    Close All Browsers

*** Test Cases ***
TC01 Admin Can Add Subject With Valid Data
    [Documentation]    ผู้ดูแลระบบสามารถเพิ่มรายวิชาใหม่ได้สำเร็จและเห็นในรายการ
    [Tags]    addsubject    positive
    Open Manage Courses Page As Admin
    ${code}=    Generate Random String    6    [NUMBERS]
    ${name}=    Set Variable    วิชาทดสอบ ${code}
    Add Subject With Custom Data    ${code}    ${name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    วิชาทดสอบการเพิ่มรายวิชา
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${code}']    10s
    Element Should Contain    xpath=//tr[td[normalize-space()='${code}']]/td[2]    ${name}

TC02 Add Subject Without Code Should Show Validation
    [Documentation]    ระบบต้องแจ้งเตือนเมื่อไม่กรอกรหัสวิชา
    [Tags]    addsubject    negative    validation
    Open Manage Courses Page As Admin
    Add Subject With Custom Data    ${EMPTY}    วิชาทดสอบไม่มีรหัส    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    ทดสอบกรณีไม่กรอกรหัส
    Wait Until Location Contains    /manage/courses/add/    10s
    Wait Until Page Contains    กรุณากรอกรหัสวิชา    10s

TC03 Add Subject With Credits Below Minimum Should Fail
    [Documentation]    ระบบต้องไม่ยอมรับหน่วยกิตที่น้อยกว่าขั้นต่ำที่กำหนด
    [Tags]    addsubject    negative    validation
    Open Manage Courses Page As Admin
    ${code}=    Generate Random String    6    [NUMBERS]
    Add Subject With Custom Data    ${code}    วิชาทดสอบหน่วยกิตต่ำ    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    0    ทดสอบกรณีหน่วยกิตต่ำกว่าเกณฑ์
    Wait Until Location Contains    /manage/courses/add/    10s
    Wait Until Page Contains    หน่วยกิตต้องไม่น้อยกว่า 1    10s

TC04 Add Subject With Duplicate Code Should Show Error
    [Documentation]    ระบบต้องป้องกันการเพิ่มรายวิชาที่มีรหัสซ้ำ
    [Tags]    addsubject    negative    duplicate
    Open Manage Courses Page As Admin
    ${code}=    Generate Random String    6    [NUMBERS]
    ${name}=    Set Variable    วิชาทดสอบซ้ำ ${code}
    Add Subject With Custom Data    ${code}    ${name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    ทดสอบการเพิ่มรายวิชารอบแรก
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${code}']    10s
    Add Subject With Custom Data    ${code}    ${name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    ทดสอบการเพิ่มรายวิชาซ้ำ
    Wait Until Location Contains    /manage/courses/add/    10s
    Wait Until Page Contains    รหัสวิชานี้มีอยู่ในระบบแล้ว    10s

*** Keywords ***
Open Manage Courses Page As Admin
    Open browser
    Login    admin    12345678
    Should See Manage Courses Dashboard
