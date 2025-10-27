*** Settings ***
Library    SeleniumLibrary
Resource   Setting.robot
Resource   Variables.robot
# สมมติว่าคุณมีคีย์เวิร์ด Login และ Open browser อยู่แล้วใน resource อื่น

*** Variables ***
# ปรับข้อความ/locator ให้ตรงระบบจริงของคุณ
${MENU_MANAGE_COURSES_TEXT}     จัดการรายวิชา
${BTN_ADD_COURSE_TEXT}          เพิ่มรายวิชาใหม่
${BTN_SAVE_TEXT}                บันทึก
${BTN_DELETE_TEXT}              ลบ
${BTN_CONFIRM_DELETE_TEXT}      ยืนยันการลบ
${MSG_DUPLICATE_ERROR}          Course และ รหัสวิชา มีอยู่แล้ว
${MSG_REQUIRED_TH}              กรุณากรอก
${PAGE_TITLE_MANAGE}            จัดการรายวิชา

# สมมติ field id ตาม Django ModelForm (ปรับได้)
${FIELD_CODE}          id=id_code
${FIELD_NAME}          id=id_name
${FIELD_DEPT}          id=id_department
${FIELD_CREDITS}       id=id_credits
${FIELD_DESC}          id=id_description
${FIELD_ACTIVE}        id=id_is_active

*** Keywords ***
Go To Manage Courses
    [Documentation]    เข้าหน้า "จัดการรายวิชา" จากเมนู
    Wait Until Element Is Visible    xpath=//a[contains(., "${MENU_MANAGE_COURSES_TEXT}")]    10s
    Click Element                    xpath=//a[contains(., "${MENU_MANAGE_COURSES_TEXT}")]
    Wait Until Page Contains         ${PAGE_TITLE_MANAGE}    10s

Open Add Course Form
    [Documentation]    กดปุ่ม "เพิ่มรายวิชาใหม่"
    Wait Until Element Is Visible    xpath=//a[contains(., "${BTN_ADD_COURSE_TEXT}")]    10s
    Click Element                    xpath=//a[contains(., "${BTN_ADD_COURSE_TEXT}")]
    # รอให้ฟอร์มแสดง (เช็ค field แรก)
    Wait Until Element Is Visible    ${FIELD_CODE}    10s

Fill Course Form
    [Arguments]    ${code}    ${name}    ${dept_label}    ${credits}    ${desc}    ${is_active}=True
    [Documentation]    กรอกข้อมูลวิชาในฟอร์ม
    # รหัสวิชา (ว่างได้ใน TC-044)
    Run Keyword If    '${code}'!=''     Input Text    ${FIELD_CODE}    ${code}

    # ชื่อวิชา
    Input Text    ${FIELD_NAME}    ${name}

    # ภาควิชา – ถ้าเป็น select ปกติ
    Run Keyword And Ignore Error    Select From List By Label    ${FIELD_DEPT}    ${dept_label}

    # หน่วยกิต
    Input Text    ${FIELD_CREDITS}    ${credits}

    # คำอธิบาย
    Input Text    ${FIELD_DESC}    ${desc}

    # สถานะเปิดใช้งาน
    Run Keyword If    ${is_active}    Select Checkbox    ${FIELD_ACTIVE}
    ...        ELSE   Unselect Checkbox    ${FIELD_ACTIVE}

Submit Course Form
    [Documentation]    กดบันทึกในฟอร์มวิชา
    Wait Until Element Is Visible    xpath=//button[@type="submit" and contains(normalize-space(.), "บันทึก")]    10s
    Click Element                    xpath=//button[@type="submit" and contains(normalize-space(.), "บันทึก")]

Return To Manage And Wait
    [Documentation]    รอให้กลับมาหน้า "จัดการรายวิชา"
    Wait Until Page Contains    ${PAGE_TITLE_MANAGE}    10s
    Sleep    0.5s

Find Row By Course Code
    [Arguments]    ${code}
    [Documentation]    คืนค่า xpath ของแถวในตาราง โดยอิงรหัสวิชา
    ${row_xpath}=    Set Variable    //table//tr[td[normalize-space()="${code}"]]
    [Return]    ${row_xpath}

Table Should Have Course
    [Arguments]    ${code}    ${name}=${EMPTY}    ${credits}=${EMPTY}
    [Documentation]    ตรวจว่าตารางมีแถววิชาตามรหัส และถ้าระบุ name/credits ให้ตรวจด้วย
    ${row}=    Find Row By Course Code    ${code}
    Wait Until Element Is Visible    xpath=${row}    10s

    # ตรวจชื่อวิชา (ถ้าระบุ)
    Run Keyword If    '${name}'!=''    Set Variable    ${cell_xpath_name}    ${row}[td[contains(normalize-space(), "${name}")]]
    Run Keyword If    '${name}'!=''    Page Should Contain Element    xpath=${cell_xpath_name}

    # ตรวจหน่วยกิต (ถ้าระบุ) — แปลงเป็นสตริงไว้ก่อน
    ${credits_str}=    Set Variable    ${credits}
    Run Keyword If    '${credits_str}'!=''    Set Variable    ${cell_xpath_credits}    ${row}[td[contains(normalize-space(), "${credits_str}")]]
    Run Keyword If    '${credits_str}'!=''    Page Should Contain Element    xpath=${cell_xpath_credits}


Table Should Not Have Course
    [Arguments]    ${code}
    ${row}=    Find Row By Course Code    ${code}
    Wait Until Page Does Not Contain Element    xpath=${row}    10s

Click Edit For Course
    [Arguments]    ${code}
    [Documentation]    คลิกปุ่มแก้ไขในแถวรหัสวิชาที่กำหนด (ปรับ class ปุ่มให้ตรงจริง)
    ${row}=    Find Row By Course Code    ${code}
    ${edit_btn}=    Set Variable    ${row}//a[contains(@class,"btn") and (contains(., "แก้ไข") or contains(@class,"warning"))]
    Scroll Element Into View    xpath=${edit_btn}
    Wait Until Element Is Visible    xpath=${edit_btn}    10s
    Click Element    xpath=${edit_btn}
    Wait Until Element Is Visible    ${FIELD_NAME}    10s

Click Delete For Course And Confirm
    [Arguments]    ${code}
    [Documentation]    ลบวิชาและกดยืนยันการลบ
    ${row}=    Find Row By Course Code    ${code}
    ${del_btn}=    Set Variable    ${row}//a[contains(@class,"btn") and (contains(., "${BTN_DELETE_TEXT}") or contains(@class,"danger"))]
    Scroll Element Into View    xpath=${del_btn}
    Wait Until Element Is Visible    xpath=${del_btn}    10s
    Click Element    xpath=${del_btn}

    # หน้า/ไดอะล็อกยืนยันการลบ
    Wait Until Page Contains    ยืนยันการลบ    10s
    Wait Until Element Is Visible    xpath=//button[contains(., "${BTN_CONFIRM_DELETE_TEXT}") or contains(@class,"btn-danger")]    10s
    Click Element                    xpath=//button[contains(., "${BTN_CONFIRM_DELETE_TEXT}") or contains(@class,"btn-danger")]

    # กลับหน้าจัดการรายวิชา
    Return To Manage And Wait

Should See Duplicate Error
    [Documentation]    ตรวจข้อความ error เมื่อข้อมูลซ้ำ
    Wait Until Page Contains    ${MSG_DUPLICATE_ERROR}    10s

Should See Required Highlight Or Message
    [Documentation]    ตรวจ error ช่องว่าง — เน้นว่าต้องมี highlight/ข้อความเตือน
    # วิธีทั่วไป: มีข้อความแจ้งเตือนภาษาไทยขึ้น เช่น "กรุณากรอก..."
    ${has_msg}=    Run Keyword And Return Status    Wait Until Page Contains    ${MSG_REQUIRED_TH}    2s
    Run Keyword If    not ${has_msg}    Log    ไม่พบข้อความทั่วไป ลองเช็คคลาส error ของ field
    # สำรอง: ตรวจว่าช่อง ${FIELD_CODE} มีคลาส invalid/ is-invalid/ error (ปรับ selector ให้ตรงจริง)
    ${cls}=    Get Element Attribute    ${FIELD_CODE}    class
    Should Contain Any    ${cls}    is-invalid    error    invalid

Should Contain Any
    [Arguments]    ${text}    @{needles}
    ${ok}=    Set Variable    ${False}
    FOR    ${n}    IN    @{needles}
        IF    '${n}' in '${text}'
            ${ok}=    Set Variable    ${True}
            Exit For Loop
        END
    END
    Run Keyword Unless    ${ok}    Fail    Expected one of ${needles} in "${text}" but not found.
