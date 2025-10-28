*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/login.robot
Resource    ../resource/addsubject.robot
Test Teardown    Close All Browsers

*** Test Cases ***
TC01 Admin Can View Manage Courses Dashboard
    [Documentation]    หน้าจัดการรายวิชาต้องแสดงตารางและปุ่มเพิ่มรายวิชาใหม่
    [Tags]    manage_courses    smoke
    Open Manage Courses Page As Admin
    Page Should Contain    จัดการรายวิชา
    Page Should Contain Element    xpath=//a[contains(@href, '/manage/courses/add/')]
    Page Should Contain Element    xpath=//table[@class='table table-hover mb-0']

TC02 Admin Can Open Course Section List
    [Documentation]    ผู้ดูแลระบบสามารถเปิดหน้าจัดการกลุ่มเรียนสำหรับรายวิชาที่สร้างใหม่ได้
    [Tags]    manage_courses    sections
    Open Manage Courses Page As Admin
    ${code}=    Generate Random String    6    [NUMBERS]
    ${name}=    Set Variable    วิชาทดสอบจัดการกลุ่ม ${code}
    Create Course And Ensure Listed    ${code}    ${name}
    Open Section List For Course Code    ${code}
    Wait Until Location Contains    /sections/    10s
    Page Should Contain    ${name}

TC03 Admin Can Open Add Course Form And Cancel
    [Documentation]    ปุ่มเพิ่มรายวิชาใหม่ต้องนำไปสู่ฟอร์ม และสามารถยกเลิกกลับมายังหน้าหลักได้
    [Tags]    manage_courses    navigation
    Open Manage Courses Page As Admin
    Click Element    xpath=//a[contains(@href, '/manage/courses/add/')]
    Wait Until Location Contains    /manage/courses/add/    10s
    Page Should Contain Element    id=id_code
    Click Element    xpath=//a[contains(@class, 'btn-secondary') and contains(., 'ยกเลิก')]
    Wait Until Location Contains    /manage/courses/    10s
    Page Should Contain    จัดการรายวิชา

*** Keywords ***
Open Manage Courses Page As Admin
    Open browser
    Login    admin    12345678
    Should See Manage Courses Dashboard

Create Course And Ensure Listed
    [Arguments]    ${code}    ${name}
    Add Subject With Custom Data    ${code}    ${name}    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    3    วิชาสำหรับทดสอบการจัดการกลุ่ม
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Contains Element    xpath=//td[normalize-space()='${code}']    10s

Open Section List For Course Code
    [Arguments]    ${code}
    ${section_xpath}=    Set Variable    //tr[td[normalize-space()='${code}']]//a[contains(@href, '/sections/')]
    Scroll Element Into View    xpath=${section_xpath}
    Wait Until Element Is Visible    xpath=${section_xpath}    10s
    Click Element    xpath=${section_xpath}
