#
# Powershell initilization script
#
# . c:\software\etc\setbin.ps1
#
$env:PYTHON3 = $env:SOFTWAREDIR + "\bin\python.bat"

$env:SOFTWAREDIR=(Split-Path (Split-Path $MyInvocation.MyCommand.Path))
$env:PATH = $env:SOFTWAREDIR + "\bin;" + $env:PATH
echo "Prefixed PATH with ""$env:SOFTWAREDIR\bin""."
