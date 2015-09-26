@echo off

if exist %~dp0\setflash.bat call %~dp0\setflash.bat

%~dp0..\chrome_45.0.2454.99\windows_5.1-x86\chrome.bat %*
