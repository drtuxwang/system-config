@echo off

if exist %~dp0\setflash.bat call %~dp0\setflash.bat

if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    %~dp0..\chromium_44.0.2383.0\windows64_5.1-x86\chromium.bat %*
) else (
    %~dp0..\chromium_44.0.2383.0\windows_5.1-x86\chromium.bat %*
)
