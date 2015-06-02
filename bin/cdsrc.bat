@echo off
rem
rem Change current working directory to source code location
rem

set CMDSET=%TEMP%\cmdset-%RANDOM%.bat
%PYTHON3% %SOFTWAREDIR%\etc\cmdenv.py %CMDSET% cd SRCDIR
call %CMDSET%
del %CMDSET%
set CMDSET=
