*** Settings ***
Library    SeleniumLibrary
Resource    Setting.robot
Resource    Variables.robot



*** Keywords ***

Click Enroll Button By Course And Section
    [Arguments]    ${course_code}    ${section}
    Wait Until Element Is Visible    xpath=//tr[td[text()='${course_code}'] and td[text()='${section}']]//button[contains(text(),'ลงทะเบียน')]    timeout=10s
    Click Button    xpath=//tr[td[text()='${course_code}'] and td[text()='${section}']]//button[contains(text(),'ลงทะเบียน')]
