@echo off

set BUSYBOX=%~dp0
copy "%~dp0\etc\init-ash" "%USERPROFILE%/.profile" > nul
%~dp0\busybox.exe ash -l %*
set BUSYBOX=
