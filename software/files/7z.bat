@echo off

if "%1"=="a" goto exec
if "%1"=="l" goto exec
if "%1"=="t" goto exec
if "%1"=="x" goto exec
    %~dp0\7z.exe a -m0=lzma2 -mmt=2 -mx=9 -myx=9 -md=128m -mfb=256 -ms=on -snh -snl -stl -y %*
    goto exit
:exec
    %~dp0\7z.exe %1 %2 %3 %4 %5 %6 %7 %8 %9
    goto exit
:exit
