*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/login.robot
Resource    ../resource/search.robot
Test Teardown    Close All Browsers

*** Test Cases ***
TC01 Student Can Search Course By Code
    [Documentation]    การค้นหาด้วยรหัสวิชาที่มีอยู่ต้องแสดงแถวที่เกี่ยวข้อง
    [Tags]    search    positive
    Open Public Course List As Student
    Search Course    156785
    Wait Until Page Contains Element    xpath=//td[normalize-space()='156785']    10s

TC02 Student Sees Empty Message When Search Not Found
    [Documentation]    เมื่อไม่พบผลลัพธ์ต้องแสดงข้อความแจ้งว่าไม่มีรายวิชา
    [Tags]    search    negative
    Open Public Course List As Student
    Search Course    ZZ9999
    Wait Until Page Contains    ยังไม่มีรายวิชาที่เปิดสอนในภาคเรียนนี้    10s
    Page Should Contain Element    xpath=//a[contains(@class, 'btn') and contains(., 'ล้างการค้นหา')]

*** Keywords ***
Open Public Course List As Student
    Open browser
    Login    65313037    Nu12345678
    Should See Public Section List Page
