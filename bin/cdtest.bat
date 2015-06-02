@echo off
rem
rem Change current working directory to test location
rem

set CMDSET=%TEMP%\cmdset-%RANDOM%.bat
%PYTHON3% %SOFTWAREDIR%\etc\cmdenv.py %CMDSET% cd TESTDIR
call %CMDSET%
del %CMDSET%
set CMDSET=
