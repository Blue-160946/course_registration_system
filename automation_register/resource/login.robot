*** Settings ***
Library    SeleniumLibrary
Resource    Setting.robot
Resource    Variables.robot


*** Keywords ***

Open browser
    ${prefs}=    Create Dictionary    profile.default_content_setting_values.media_stream_camera=1    profile.default_content_setting_values.media_stream_microphone=1
        ${options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
        Call Method    ${options}    add_experimental_option    prefs    ${prefs}
        
        # ใช้ fake media devices แทนอุปกรณ์จริง
        Call Method    ${options}    add_argument    --use-fake-ui-for-media-stream
        Call Method    ${options}    add_argument    --use-fake-device-for-media-stream
        Call Method    ${options}    add_argument    --fake-video-capture-device
        Call Method    ${options}    add_argument    --fake-audio-capture-device
        
        Create WebDriver    Chrome    options=${options}
        Maximize Browser Window
        Go To    ${URL}    


Login
    [Arguments]    ${username}=${EMPTY}    ${password}=${EMPTY}    ${expected}=True
    Sleep    2s
    Click Element    //*[@id="navbarNav"]/ul[2]/li/a
    Sleep    1s
    Input Text    id=id_username    ${username}
    Sleep    1s
    Input Text    id=id_password    ${password}
    Wait Until Element Is Visible    xpath=//form//button[@type="submit"]    timeout=10s
    Click Element                    xpath=//form//button[@type="submit"]
    Sleep   3s

Should Stay On Login Page
    [Documentation]    ยังคงอยู่ที่หน้าล็อกอิน
    Wait Until Location Contains    /users/login/    5s
    Wait Until Element Is Visible    css=form.needs-validation    5s

Should See Manage Courses Dashboard
    [Documentation]    หน้าเจ้าาหน้าที่หลังล็อกอินควรเป็นหน้าจัดการรายวิชา
    Wait Until Location Contains    /manage/courses/    10s
    Wait Until Page Contains    จัดการรายวิชา    10s

Should See Public Section List Page
    [Documentation]    หน้าของนิสิตหลังล็อกอินควรเป็นหน้ารายวิชาที่เปิดลงทะเบียน
    Wait Until Location Contains    /manage/courses/register/    10s
    Wait Until Page Contains    รายวิชาที่เปิดลงทะเบียน    10s

Should See Invalid Feedback For Field
    [Arguments]    ${field_id}    ${expected_text}
    [Documentation]    ตรวจสอบว่า invalid feedback ของฟิลด์ปรากฏจริงบนหน้าจอ
    Wait Until Element Is Visible    css=form.was-validated    5s
    ${selector}=    Set Variable    #${field_id} + .invalid-feedback
    ${display}=    Execute Javascript    return window.getComputedStyle(document.querySelector(arguments[0])).display;    ${selector}
    Should Be Equal    ${display}    block
    Element Should Contain    xpath=//input[@id="${field_id}"]/following-sibling::div[contains(@class,"invalid-feedback")]    ${expected_text}

Should See Login Error Message
    [Arguments]    ${expected_message}
    [Documentation]    ตรวจสอบว่ามีข้อความแจ้งเตือนความผิดพลาดหลังล็อกอินไม่สำเร็จ
    Wait Until Element Is Visible    css=.alert.alert-danger    10s
    Element Should Contain    css=.alert.alert-danger    ${expected_message}
