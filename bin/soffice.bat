@echo off
echo > .~lock.#
for %%f in (.~lock.*#) do del %%f
%~dp0..\libreoffice_5.0.6.3\windows_5.1-x86\soffice.bat %*
