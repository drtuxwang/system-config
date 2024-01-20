@echo off

if "%1"=="" goto shell
    powershell.exe -command start-process cmd.exe -argumentlist "\"/r %*\"" -verb runas
    goto end
:shell
    powershell.exe -command start-process cmd.exe -verb runas
end
