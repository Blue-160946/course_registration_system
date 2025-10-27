*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/view_data.robot

*** Test Cases ***
TC01 view data
    [Documentation]    ดูข้อมูล
    [Tags]   valid
    Click menu view data
    Click Student Detail By ID

