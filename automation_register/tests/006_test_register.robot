*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/register.robot

*** Test Cases ***
TC01 register
    [Documentation]    ลงทะเบียนเรียน
    [Tags]   user_test
    Click Enroll Button By Course And Section    CS920    3


