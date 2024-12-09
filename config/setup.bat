@echo off

ver

for /f %%a in ('dir /b /s ..\pool\software\7zip_*-windows-x86.exe') do (
    echo Running "%%a" installer...
    "%%a" -oc:\software -y
)

if "%PROCESSOR_ARCHITECTURE%"=="AMD64" goto win64
if "%PROCESSOR_ARCHITEW6432%"=="AMD64" goto win64
    for /f %%a in ('dir /b /s ..\pool\software\busybox_*-windows-x86.7z') do (
        echo Installing "%%a" archive...
        call c:\software\bin\7z.bat x -oc:\software -y "%%a"
    )
    goto install
:win64
    for /f %%a in ('dir /b /s ..\pool\software\busybox_*-windows64-x86.7z') do (
        echo Installing "%%a" archive...
        call c:\software\bin\7z.bat x -oc:\software -y "%%a"
    )
:install

rem echo.
rem echo Running "net use h: \\vboxsvr\shared"...
rem net use h: \\vboxsvr\shared 2> nul

if exist %~dp0\setupwin.ash c:\software\bin\busybox %~dp0\setupwin.ash
if exist %~dp0\config\setupwin.ash c:\software\bin\busybox %~dp0\config\setupwin.ash

echo DONE!
