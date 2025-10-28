*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/login.robot
Resource    ../resource/view_data.robot
Test Teardown    Close All Browsers

*** Test Cases ***
TC01 Admin Can View Student List
    [Documentation]    หน้าข้อมูลนิสิตต้องแสดงหัวตารางและรายชื่ออย่างน้อยหนึ่งรายการ
    [Tags]    view_data    list
    Open Student List Page As Admin
    Page Should Contain    ข้อมูลนิสิต
    Page Should Contain Element    xpath=//table[contains(@class, 'table-hover')]
    Wait Until Page Contains Element    xpath=(//table//tbody/tr)[1]    10s
    ${first_student_id}=    Get Text    xpath=(//table//tbody/tr[1]/td[1])[1]
    Should Not Be Empty    ${first_student_id}

TC02 Admin Can Open Student Detail And Return
    [Documentation]    สามารถเปิดรายละเอียดนิสิตจากรายการและกลับมายังหน้ารายการได้
    [Tags]    view_data    detail
    Open Student List Page As Admin
    ${student_id}=    Get Text    xpath=(//table//tbody/tr[1]/td[1])[1]
    Click Student Detail By ID    ${student_id}
    Page Should Contain    รายละเอียดนิสิต
    Page Should Contain    ${student_id}
    Click Element    xpath=//a[contains(@class, 'btn-outline-orange')]
    Wait Until Location Contains    /users/students/    10s
    Page Should Contain    ข้อมูลนิสิต

*** Keywords ***
Open Student List Page As Admin
    Open browser
    Login    admin    12345678
    Should See Manage Courses Dashboard
    Click menu view data
    Wait Until Location Contains    /users/students/    10s
