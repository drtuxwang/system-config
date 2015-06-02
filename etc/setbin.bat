@echo off
rem
rem Command shell initilization script
rem
rem c:\software\etc\setbin.bat
rem

set SOFTWAREDIR=%~dp0..
set PATH=%SOFTWAREDIR%\bin;%PATH%
echo Prefixed PATH with "%SOFTWAREDIR%\bin".
