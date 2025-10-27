*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/search.robot

*** Test Cases ***
TC01 search
    [Documentation]    ค้นหาวิชา
    [Tags]   user_test    search_test
    Search Course    CS920



