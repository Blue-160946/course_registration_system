*** Settings ***
Library    SeleniumLibrary
Resource    Setting.robot
Resource    Variables.robot



*** Keywords ***
Edit Subject Random
    [Documentation]    แก้ไขข้อมูลวิชาแบบสุ่ม
    Wait Until Element Is Visible    xpath=/html/body/main/div/div[2]/div/div/table/tbody/tr[1]/td[6]/div/a[1]   timeout=10s
    Click Element    xpath=//tr[td[normalize-space()='ฐานข้อมูล']]//a[contains(@href, '/edit/')]
    Wait Until Element Is Visible    xpath=/html/body/main/div/div/div    timeout=10s
    # รหัสวิชา
    ${random_code}=    Evaluate    'CS' + str(random.randint(100, 999))    modules=random
    Input Text    id=id_code    ${random_code}
    # ชื่อวิชา
    ${subjects}=    Create List    การเขียนโปรแกรมเบื้องต้น    คณิตศาสตร์คอมพิวเตอร์    โครงสร้างข้อมูล    ฐานข้อมูล    ปัญญาประดิษฐ์
    ${random_subject}=    Evaluate    random.choice($subjects)    modules=random
    Input Text    id=id_name    ${random_subject}
    # เลือกภาควิชา
    ${departments}=    Create List    วิทยาการคอมพิวเตอร์    วิศวกรรมคอมพิวเตอร์    เทคโนโลยีสารสนเทศ
    ${random_dept}=    Evaluate    random.choice($departments)    modules=random
    Select From List By Label    id=id_department    ${random_dept}
    # หน่วยกิต
    ${random_credits}=    Evaluate    random.randint(1, 4)    modules=random
    Input Text    id=id_credits    ${random_credits}
    # คำอธิบาย
    ${descriptions}=    Create List    วิชานี้สอนพื้นฐานการเขียนโปรแกรม    วิชาเรียนเกี่ยวกับโครงสร้างข้อมูล    วิชาพื้นฐานคณิตศาสตร์    วิชาเกี่ยวกับการจัดการฐานข้อมูล
    ${random_desc}=    Evaluate    random.choice($descriptions)    modules=random
    Input Text    id=id_description    ${random_desc}
    # ตรวจสอบ checkbox ว่าติ๊กอยู่หรือไม่
    Checkbox Should Be Selected    id=id_is_active
    # กดปุ่ม "บันทึก"
    Click Button    xpath=//button[@type='submit' and contains(., 'บันทึก')]

Edit Subject With Parameters
    [Documentation]    แก้ไขข้อมูลวิชาด้วยพารามิเตอร์ที่กำหนด (ดีฟอลต์เลือกวิชา 'ฐานข้อมูล')
    [Arguments]    ${code}    ${name}    ${department}    ${credits}    ${description}
    Open Subject Edit Form By Course Name    ฐานข้อมูล
    Fill Subject Edit Form    ${code}    ${name}    ${department}    ${credits}    ${description}


Open Subject Edit Form By Course Name
    [Documentation]    เปิดหน้าฟอร์มแก้ไขโดยอ้างอิงชื่อวิชา (normalize-space)
    [Arguments]    ${course_name}
    ${edit_xpath}=    Set Variable    //tr[td[normalize-space()='${course_name}']]//a[contains(@href, '/edit/')]
    Scroll Element Into View    xpath=${edit_xpath}
    Wait Until Element Is Visible    xpath=${edit_xpath}    timeout=10s
    Click Element    xpath=${edit_xpath}
    Wait Until Element Is Visible    id=id_name    timeout=10s


Open Subject Edit Form By Course Code
    [Documentation]    เปิดหน้าฟอร์มแก้ไขโดยอ้างอิงรหัสวิชา
    [Arguments]    ${course_code}
    ${edit_xpath}=    Set Variable    //tr[td[normalize-space()='${course_code}']]//a[contains(@href, '/edit/')]
    Scroll Element Into View    xpath=${edit_xpath}
    Wait Until Element Is Visible    xpath=${edit_xpath}    timeout=10s
    Click Element    xpath=${edit_xpath}
    Wait Until Element Is Visible    id=id_name    timeout=10s


Fill Subject Edit Form
    [Documentation]    กรอกข้อมูลลงในฟอร์มแก้ไขวิชาและบันทึก
    [Arguments]    ${code}    ${name}    ${department}    ${credits}    ${description}
    # รหัสวิชา
    Clear Element Text    id=id_code
    Input Text    id=id_code    ${code}
    # ชื่อวิชา
    Clear Element Text    id=id_name
    Input Text    id=id_name    ${name}
    # เลือกภาควิชา
    Select From List By Label    id=id_department    ${department}
    # หน่วยกิต
    Clear Element Text    id=id_credits
    Input Text    id=id_credits    ${credits}
    # คำอธิบาย
    Clear Element Text    id=id_description
    Input Text    id=id_description    ${description}
    # ตรวจสอบ checkbox ว่าติ๊กอยู่หรือไม่
    Checkbox Should Be Selected    id=id_is_active
    # กดปุ่ม "บันทึก"
    Click Button    xpath=//button[@type='submit' and contains(., 'บันทึก')]
