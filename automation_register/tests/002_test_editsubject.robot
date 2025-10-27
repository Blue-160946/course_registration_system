*** Settings ***
Resource    ../resource/Setting.robot
Resource    ../resource/Variables.robot
Resource    ../resource/editsubject.robot

*** Test Cases ***
TC01 editsubject
    [Documentation]    แก้ไขข้อมูลวิชา
    [Tags]   valid    testcase2
    Edit Subject With Parameters    254371    Software Engineering   วิทยาการณ์คอมพิวเตอร์และเทคโนโลยีสารสนเทศ    4    วิชานี้สอนพื้นฐานการเขียนโปรแกรม 