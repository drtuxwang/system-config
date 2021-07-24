@echo off

ver

for /f %%a in ('dir /b /s ..\software\7zip_*_win*x86.exe') do (
    echo Running "%%a" installer...
    "%%a" -oc:\software -y
)

if "%PROCESSOR_ARCHITECTURE%"=="AMD64" goto win64
if "%PROCESSOR_ARCHITEW6432%"=="AMD64" goto win64
    for /f %%a in ('dir /b /s ..\software\busybox_*_win??x86.7z') do (
        echo Installing "%%a" archive...
        call c:\software\bin\7z.bat x -oc:\software -y "%%a"
    )
    goto install
:win64
    for /f %%a in ('dir /b /s ..\software\busybox_*_win64*x86.7z') do (
        echo Installing "%%a" archive...
        call c:\software\bin\7z.bat x -oc:\software -y "%%a"
    )
:install

echo.
echo Running "net use s: \\vboxsvr\shared"...
net use s: \\vboxsvr\shared 2> nul

c:\software\bin\busybox %~dp0\winsetup.sh

echo DONE!
