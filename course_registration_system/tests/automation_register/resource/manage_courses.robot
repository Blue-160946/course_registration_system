*** Settings ***
Library    SeleniumLibrary
Resource    Setting.robot
Resource    Variables.robot



*** Keywords ***

Click menu manage courses
    [Documentation]   คลิกที่เมนูจัดการวิชา
    Click Element    xpath=//a[contains(., "จัดการรายวิชา")]

Click manage courses
    [Documentation]   คลิกที่จัดการกลุ่มเรียน
    ${xpath}=    Set Variable    //tr[td[contains(text(), "CS540")]]//a[contains(@href, "/sections/") and contains(., "จัดการกลุ่มเรียน")]
    Scroll Element Into View    xpath=${xpath}
    Wait Until Element Is Visible    xpath=${xpath}    timeout=10s
    Click Element    xpath=${xpath}

Add manage courses
    [Documentation]   เพิ่มวิชาใหม่
    Wait Until Element Is Visible    xpath=//a[contains(@href, "/manage/courses/7/add-section/") and contains(., "เพิ่มกลุ่มเรียนใหม่")]    10s
    Click Element    xpath=//a[contains(@href, "/manage/courses/7/add-section/") and contains(., "เพิ่มกลุ่มเรียนใหม่")]

     # เลือกภาคเรียน
    Wait Until Element Is Visible    id=id_semester    10s
    Select From List By Value    id=id_semester    1

    # กรอกกลุ่มเรียน
    Input Text    id=id_section_number    1

    # เลือกห้องเรียน
    Select From List By Value    id=id_room    1

    # กรอกจำนวนที่รับ
    Input Text    id=id_capacity    30

    # เลือกอาจารย์ผู้สอน (หลายตัวเลือก)
    # ถ้า select2 ต้องใช้การคลิกแบบพิเศษ
    Click Element    css=#id_instructors + span.select2-container
    Sleep    2s
    Wait Until Element Is Visible    css=textarea.select2-search__field    10s
    Input Text    css=textarea.select2-search__field    พิบัติภัย วงศ์ตระกูล
    Press Keys    css=textarea.select2-search__field    ENTER


    # เลือกวันคาบเรียน
    Select From List By Value    id=id_class_times-0-day    MON
t
    # กรอกเวลาเริ่มต้นและเวลาสิ้นสุด
    Input Text    id=id_class_times-0-start_time    08:30
    Input Text    id=id_class_times-0-end_time      10:00

    # กดบันทึก
    Click Button    xpath=//button[@type='submit' and contains(., 'บันทึก')]

    # รอหน้า redirect หรือยืนยันการบันทึกสำเร็จ
    # Wait Until Page Contains    จัดการรายวิชา    10s



Edit manage courses
    [Documentation]   แก้ไขวิชา
    Wait Until Element Is Visible    xpath=//table//tbody/tr[td[contains(text(), 'Sec 01')]]//a[contains(@class, 'btn-outline-warning')]    10s
    Click Element    xpath=//table//tbody/tr[td[contains(text(), 'Sec 01')]]//a[contains(@class, 'btn-outline-warning')]

   
    Input Text    id=id_capacity    99

    # กดบันทึก
    Click Button    xpath=//button[@type='submit' and contains(., 'บันทึก')]

    # รอหน้า redirect หรือยืนยันการบันทึกสำเร็จ
    # Wait Until Page Contains    วิชาทดสอบแก้ไข    10s



Del manage courses
    [Documentation]   ลบกลุ่มเรียน
    Wait Until Element Is Visible    xpath=//table//tbody/tr[1]//a[contains(@class, 'btn-outline-danger')]    10s
    Click Element    xpath=//table//tbody/tr[1]//a[contains(@class, 'btn-outline-danger')]
    Sleep    2s

    Click Button    xpath=//button[@type='submit' and contains(@class, 'btn-danger') and contains(text(), 'ยืนยันการลบ')]


