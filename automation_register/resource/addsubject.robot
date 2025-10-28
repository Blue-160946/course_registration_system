*** Settings ***
Library    SeleniumLibrary
Resource    Setting.robot
Resource    Variables.robot



*** Keywords ***
Add Subject With Random Data
    [Documentation]    กรอกข้อมูลวิชาใหม่แบบสุ่ม
    
    Wait Until Element Is Visible    xpath=/html/body/main/div/div[1]/a    timeout=10s
    Click Element                    xpath=/html/body/main/div/div[1]/a
    Wait Until Element Is Visible    xpath=/html/body/main/div/div/div    timeout=10s
    
    # Generate random values
    ${random_code}=    Evaluate    'CS' + str(__import__('random').randint(100, 999))
    ${random_credits}=    Evaluate    __import__('random').randint(1, 6)
    ${subjects}=    Create List    การเขียนโปรแกรมเบื้องต้น    โครงสร้างข้อมูล    ฐานข้อมูล    เครือข่าย    ปัญญาประดิษฐ์    การพัฒนาเว็บ
    ${departments}=    Create List    วิทยาการคอมพิวเตอร์และเทคโนโลยีสารสนเทศ    ชีวะ    เคมี
    ${descriptions}=    Create List    วิชานี้สอนพื้นฐานการเขียนโปรแกรม    เรียนรู้โครงสร้างข้อมูลและอัลกอริทึม    ศึกษาการจัดการฐานข้อมูล    เรียนรู้เกี่ยวกับเครือข่ายคอมพิวเตอร์
    
    ${random_subject}=    Evaluate    __import__('random').choice($subjects)
    ${random_department}=    Evaluate    __import__('random').choice($departments)
    ${random_description}=    Evaluate    __import__('random').choice($descriptions)
    
    # รหัสวิชา
    Input Text    id=id_code    ${random_code}
    # ชื่อวิชา
    Input Text    id=id_name    ${random_subject}
    # เลือกภาควิชา
    Select From List By Label    id=id_department    ${random_department}
    # หน่วยกิต
    Input Text    id=id_credits    ${random_credits}
    # คำอธิบาย
    Input Text    id=id_description    ${random_description}
    # ตรวจสอบ checkbox ว่าติ๊กอยู่หรือไม่
    Checkbox Should Be Selected    id=id_is_active
    # กดปุ่ม "บันทึก"
    Click Button    xpath=//button[@type='submit' and contains(., 'บันทึก')]

Add Subject With Custom Data
    [Documentation]    กรอกข้อมูลวิชาใหม่ด้วยข้อมูลที่กำหนด
    [Arguments]    ${code}    ${name}    ${department}    ${credits}    ${description}
    
    Wait Until Element Is Visible    xpath=/html/body/main/div/div[1]/a    timeout=10s
    Click Element     
    ...               xpath=/html/body/main/div/div[1]/a
    Wait Until Element Is Visible    xpath=/html/body/main/div/div/div    timeout=10s
    
    # รหัสวิชา
    Input Text    id=id_code    ${code}
    # ชื่อวิชา
    Input Text    id=id_name    ${name}

    Wait Until Element Is Visible    id=id_department    10s
    # เลือกภาควิชา
    Select From List By Label    id=id_department    ${department}
    # หน่วยกิต
    Input Text    id=id_credits    ${credits}
    # คำอธิบาย
    Input Text    id=id_description    ${description}
    # ตรวจสอบ checkbox ว่าติ๊กอยู่หรือไม่
    Checkbox Should Be Selected    id=id_is_active
    # กดปุ่ม "บันทึก"
    Click Button    xpath=//button[@type='submit' and contains(., 'บันทึก')]

    Sleep    3s


