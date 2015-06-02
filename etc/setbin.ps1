#
# Powershell initilization script
#
# . c:\software\etc\setbin.ps1
#
$env:PYTHON3 = $env:SOFTWAREDIR + "\bin\python.bat"

$env:SOFTWAREDIR=(Split-Path (Split-Path $MyInvocation.MyCommand.Path))
$env:PATH = $env:SOFTWAREDIR + "\bin;" + $env:PATH
echo "Prefixed PATH with ""$env:SOFTWAREDIR\bin""."

#
# mktest/cdtest, mksrc/cdsrc, mkinst/cdinst
#
function mksrc { $env:SRCDIR = $pwd; echo "New SRCDIR: $env:SRCDIR" }
function cdsrc { echo "Using SRCDIR: $env:SRCDIR"; & cd $env:SRCDIR }
function mkinst { $env:INSTDIR = $pwd; echo "New INSTDIR: $env:INSTDIR" }
function cdinst { echo "Using INSTDIR: $env:INSTDIR"; & cd $env:INSTDIR }
function mktest { $env:TESTDIR = $pwd; echo "New TESTDIR: $env:TESTDIR" }
function cdtest { echo "Using TESTDIR: $env:TESTDIR"; & cd $env:TESTDIR }
