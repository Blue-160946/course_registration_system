*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/login.robot
Resource    ../resource/addsubject.robot
Resource    ../resource/delsubject.robot
Test Teardown    Close All Browsers

*** Test Cases ***
TC01 Admin Can Delete Subject Successfully
    [Documentation]    ผู้ดูแลระบบสามารถลบรายวิชาที่เพิ่งสร้างได้และไม่พบในรายการอีก
    [Tags]    delsubject    positive
    Open Manage Courses Page As Admin
    ${code}=    Generate Random String    6    [NUMBERS]
    ${name}=    Set Variable    วิชาทดสอบลบ ${code}
    Add Subject With Custom Data    ${code}    ${name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    วิชาสำหรับทดสอบการลบ
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${code}']    10s
    Delete Course By Code    ${code}
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Does Not Contain    ${code}    10s

TC02 Admin Cancels Deletion And Course Remains
    [Documentation]    เมื่อยกเลิกการลบ รายวิชาต้องยังคงอยู่ในรายการ
    [Tags]    delsubject    negative    cancel
    Open Manage Courses Page As Admin
    ${code}=    Generate Random String    6    [NUMBERS]
    ${name}=    Set Variable    วิชาทดสอบยกเลิก ${code}
    Add Subject With Custom Data    ${code}    ${name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    วิชาสำหรับทดสอบยกเลิกการลบ
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${code}']    10s
    Open Delete Confirmation For Course    ${code}
    Wait Until Page Contains    คุณแน่ใจหรือไม่ว่าจะลบรายวิชานี้?    10s
    Click Element    xpath=//a[contains(@class, 'btn-secondary') and contains(., 'ยกเลิก')]
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${code}']    10s

*** Keywords ***
Open Manage Courses Page As Admin
    Open browser
    Login    admin    12345678
    Should See Manage Courses Dashboard

Open Delete Confirmation For Course
    [Arguments]    ${course_code}
    ${delete_xpath}=    Set Variable    //tr[td[normalize-space()='${course_code}']]//a[contains(@class, 'btn-outline-danger')]
    Scroll Element Into View    xpath=${delete_xpath}
    Wait Until Element Is Visible    xpath=${delete_xpath}    10s
    Click Element    xpath=${delete_xpath}
    Wait Until Location Contains    /delete/    10s
