*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/manage_courses.robot

*** Test Cases ***
TC01 add manage courses
    [Documentation]    จัดการรายวิชา
    # [Tags]   valid
    Click menu manage courses
    Click manage courses
    Add manage courses



TC02 edit manage courses
    [Documentation]    แก้ไขกลุ่มเรียน
    # [Tags]   valid
    Click menu manage courses
    Click manage courses
    # Edit manage courses
    # Del manage courses