@echo off
if not "%PROCESSOR_ARCHITECTURE%"=="AMD64" goto x86
if not exist %~dp0..\python_2.7.11\windows_5.1-x86\python.exe goto x86
    %~dp0..\python_2.7.11\windows_5.1-x86\python.exe -B %*
    goto end
:x86
    %~dp0..\python_2.7.11\windows_5.1-x86\python.exe -B %*
:end
