@echo off
echo > .~lock.#
for %%f in (.~lock.*#) do del %%f
%~dp0..\libreoffice_4.4.4.3\windows_5.1-x86\soffice.bat %*
