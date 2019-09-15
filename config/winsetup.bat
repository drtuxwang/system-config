@echo off

ver
for /f %%a in ('dir /b /s ..\software\busybox_*_win51x86.exe') do (
    echo Running "%%a" installer...
    "%%a" -oc:\software -y
)

c:\software\bin\busybox %~dp0\winsetup.sh

echo DONE!
