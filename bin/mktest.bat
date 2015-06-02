@echo off
rem
rem Select current working directory as test case location
rem

set CMDSET=%TEMP%\cmdset-%RANDOM%.bat
%PYTHON3% %SOFTWAREDIR%\etc\cmdenv.py %CMDSET% set TESTDIR
call %CMDSET%
del %CMDSET%
set CMDSET=
