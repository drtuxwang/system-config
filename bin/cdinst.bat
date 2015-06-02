@echo off
rem
rem Change current working directory to installation location
rem

set CMDSET=%TEMP%\cmdset-%RANDOM%.bat
%PYTHON3% %SOFTWAREDIR%\etc\cmdenv.py %CMDSET% cd INSTDIR
call %CMDSET%
del %CMDSET%
set CMDSET=
