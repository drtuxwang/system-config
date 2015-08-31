@echo off

set FLASHVER=18.0.0.232
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set FLASHLIB=%~dp0..\flash_%FLASHVER%\windows64_5.1-x86\pepflashplayer.dll
) else (
    set FLASHLIB=%~dp0..\flash_%FLASHVER%\windows_5.1-x86\pepflashplayer.dll
)

if not exist %FLASHLIB% (
    set FLASHLIB=
    set FLASHVER=
)
