*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/delsubject.robot

*** Test Cases ***
TC01 delsubject
    [Documentation]    ลบข้อมูลวิชา
    [Tags]   valid    testcase3
    Delete Course By Code    254371
