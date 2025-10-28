*** Settings ***
Library    SeleniumLibrary
Resource    Setting.robot
Resource    Variables.robot




*** Keywords ***

Click menu view data
    [Documentation]    คลิกเมนูจัดดูข้อมูลนิสิต
    # พราะ text() ของ <a> นี้ไม่ได้เป็นแค่ "ดูข้อมูลนิสิต" อย่างเดียว — มันมี <i> แทรกอยู่ก่อนด้วย ซึ่งทำให้ text() ไม่ตรงกับ "ดูข้อมูลนิสิต" 
    # . (dot) จะ match กับข้อความทั้งหมดภายใน <a>, รวมทั้งที่อยู่ใน tag ย่อยอย่าง <i>
    Click Element    xpath=//a[contains(., 'ดูข้อมูลนิสิต')]

    Sleep    3s

Click Student Detail By ID
    [Arguments]    ${student_id}
    ${detail_xpath}=    Set Variable    //tr[td[normalize-space()='${student_id}']]//a[contains(., 'ดูรายละเอียด')]
    Wait Until Element Is Visible    xpath=${detail_xpath}    timeout=10s
    Scroll Element Into View    xpath=${detail_xpath}
    Click Element    xpath=${detail_xpath}
    Wait Until Page Contains    รายละเอียดนิสิต    10s
