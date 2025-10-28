*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/login.robot
Resource    ../resource/register.robot
Test Teardown    Close All Browsers

*** Test Cases ***
TC01 Student Can View Available Courses
    [Documentation]    หน้าลงทะเบียนต้องแสดงตารางรายวิชาให้ผู้ใช้ทั่วไปเห็น
    [Tags]    register    list
    Open Public Course List As Student
    Page Should Contain    รายวิชาที่เปิดลงทะเบียน
    Page Should Contain Element    xpath=//table[contains(@class, 'table-hover')]
    Page Should Contain Element    xpath=//th[normalize-space()='รหัสวิชา']

TC02 Student Can Enroll In Section
    [Documentation]    เมื่อลงทะเบียนสำเร็จควรเห็นสถานะลงทะเบียนแล้วที่แถวของรายวิชา
    [Tags]    register    enroll
    Open Public Course List As Student
    ${row_xpath}=    Set Variable    //tr[td[normalize-space()='254371'] and td[normalize-space()='2']]
    ${badge_xpath}=    Set Variable    ${row_xpath}//span[contains(@class, 'badge') and contains(., 'ลงทะเบียนแล้ว')]
    ${button_xpath}=    Set Variable    ${row_xpath}//button[contains(., 'ลงทะเบียน')]
    Wait Until Page Contains Element    xpath=${row_xpath}    10s
    ${already_enrolled}=    Run Keyword And Return Status    Element Should Be Visible    xpath=${badge_xpath}
    Run Keyword Unless    ${already_enrolled}    Wait Until Element Is Visible    xpath=${button_xpath}    10s
    Run Keyword Unless    ${already_enrolled}    Click Enroll Button By Course And Section    254371    2
    Wait Until Location Contains    /manage/courses/register/    10s
    Wait Until Element Is Visible    xpath=${badge_xpath}    10s

*** Keywords ***
Open Public Course List As Student
    Open browser
    Login    65313037    Nu12345678
    Should See Public Section List Page
