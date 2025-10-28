*** Settings ***
Library    SeleniumLibrary
Resource    Setting.robot
Resource    Variables.robot



*** Keywords ***

Search Course
    [Arguments]    ${keyword}
    Wait Until Element Is Visible    css=input[placeholder*="ค้นหารหัสวิชาหรือชื่อวิชา"]    timeout=10s
    Input Text    css=input[placeholder*="ค้นหารหัสวิชาหรือชื่อวิชา"]    ${keyword}
    Click Button    xpath=//button[contains(text(), "ค้นหา")]
    Sleep    5s