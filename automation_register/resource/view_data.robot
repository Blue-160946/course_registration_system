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
 
    Wait Until Element Is Visible    xpath=//tr[td[normalize-space(text())='${653211}']]//a[contains(., 'ดูรายละเอียด')]    timeout=10s
    Scroll Element Into View         xpath=//tr[td[normalize-space(text())='${653211}']]//a[contains(., 'ดูรายละเอียด')]
    Click Element                    xpath=//tr[td[normalize-space(text())='${653211}']]//a[contains(., 'ดูรายละเอียด')]
    Sleep    2s
