@echo off
rem
rem Select current working directory as source code location
rem

set CMDSET=%TEMP%\cmdset-%RANDOM%.bat
%PYTHON3% %SOFTWAREDIR%\etc\cmdenv.py %CMDSET% set SRCDIR
call %CMDSET%
del %CMDSET%
set CMDSET=

