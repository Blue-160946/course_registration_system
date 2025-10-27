*** Settings ***
Library    SeleniumLibrary
Resource    Setting.robot
Resource    Variables.robot



*** Keywords ***
Delete Course By Code
    [Arguments]    ${course_code}
    ${xpath}=    Set Variable    //tr[td[contains(text(), "${course_code}")]]//a[contains(@href, '/delete/') and contains(@class, 'btn-outline-danger')]

    Wait Until Element Is Visible    xpath=${xpath}    timeout=10s
    Click Element    xpath=${xpath}

    Wait Until Element Is Visible    xpath=/html/body/main    timeout=10s
    Sleep    1s
    Click Button    xpath=//button[@type='submit' and contains(., 'ยืนยันการลบ')]
