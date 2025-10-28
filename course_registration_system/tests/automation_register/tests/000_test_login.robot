*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/login.robot
Test Teardown    Close All Browsers



*** Test Cases ***

TC015 Admin Login With Valid Credentials
    [Documentation]    ผู้ดูแลระบบเข้าสู่ระบบด้วยข้อมูลที่ถูกต้องและเห็นหน้าจัดการรายวิชา
    [Tags]    login    positive    admin
    Open browser
    Login    admin    12345678
    Should See Manage Courses Dashboard

TC016 Student Login With Valid Credentials
    [Documentation]    ผู้ใช้ทั่วไปเข้าสู่ระบบด้วยข้อมูลที่ถูกต้องและเห็นหน้ารายวิชาที่เปิดลงทะเบียน
    [Tags]    login    positive    student
    Open browser
    Login    65313037    Nu12345678
    Should See Public Section List Page

TC017 Login Without Username
    [Documentation]    ไม่กรอกชื่อผู้ใช้แต่กรอกรหัสผ่าน ระบบต้องแจ้งเตือนให้กรอกชื่อผู้ใช้
    [Tags]    login    negative    validation
    Open browser
    Login    ${EMPTY}    12345678
    Should Stay On Login Page
    Wait Until Element Is Visible    id=id_username    10s
     Wait Until Page Contains    กรุณากรอกชื่อผู้ใช้    10s
    Page Should Contain    กรุณากรอกชื่อผู้ใช้

TC018 Login Without Password
    [Documentation]    กรอกชื่อผู้ใช้แต่ไม่กรอกรหัสผ่าน ระบบต้องแจ้งเตือนให้กรอกรหัสผ่าน
    [Tags]    login    negative    validation
    Open browser
    Login    admin    ${EMPTY}
    Should Stay On Login Page
    Wait Until Element Is Visible    id=id_password    10s
    Wait Until Page Contains    กรุณากรอกรหัสผ่าน    10s
    Page Should Contain    กรุณากรอกรหัสผ่าน


TC019 Login Without Username And Password
    [Documentation]    ไม่กรอกทั้งชื่อผู้ใช้และรหัสผ่าน ระบบต้องแจ้งเตือนทั้งสองฟิลด์
    [Tags]    login    negative    validation
    Open browser
    Login    ${EMPTY}    ${EMPTY}
    Should Stay On Login Page
     Page Should Contain    กรุณากรอกชื่อผู้ใช้
     Page Should Contain    กรุณากรอกรหัสผ่าน

TC020 Login With Whitespace Only
    [Documentation]    กรอกช่องด้วยช่องว่าง ระบบต้องไม่ยอมให้เข้าสู่ระบบและแสดงข้อความผิดพลาด
    [Tags]    login    negative    validation
    Open browser
    Login    ${SPACE}    ${SPACE}
    Should Stay On Login Page
    Should See Login Error Message    ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง

TC021 Login With Invalid Password
    [Documentation]    กรอกรหัสผ่านไม่ถูกต้อง ระบบต้องไม่ยอมให้เข้าสู่ระบบและแสดงข้อความผิดพลาด
    [Tags]    login    negative
    Open browser
    Login    admin    WrongPassword123
    Should Stay On Login Page
    Should See Login Error Message    ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง
