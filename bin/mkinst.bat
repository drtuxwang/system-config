@echo off
rem
rem Select current working directory as installation location
rem

set CMDSET=%TEMP%\cmdset-%RANDOM%.bat
%PYTHON3% %SOFTWAREDIR%\etc\cmdenv.py %CMDSET% set INSTDIR
call %CMDSET%
del %CMDSET%
set CMDSET=
