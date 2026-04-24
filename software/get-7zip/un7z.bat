@echo off

if "%1"=="-v" goto view
    %~dp0\7z.exe x -y %*
    goto exit
:view
    %~dp0\7z.exe l %2 %3 %4 %5 %6 %7 %8 %9
    goto exit
:exit
