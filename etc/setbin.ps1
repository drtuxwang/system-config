#
# Powershell initilization script
#
# . c:\software\etc\setbin.ps1
#
$env:PYTHON3 = $env:SOFTWAREDIR + "\bin\python.bat"

$env:SOFTWAREDIR=(Split-Path (Split-Path $MyInvocation.MyCommand.Path))
$env:PATH = $env:SOFTWAREDIR + "\bin;" + $env:PATH
echo "Prefixed PATH with ""$env:SOFTWAREDIR\bin""."

# mkinst, cdinst, mksrc, cdsrc, mktest, cdtest, scd
$env:cdinst = $pwd
$env:cdsrc = $pwd
$env:cdtest = $pwd
function mkinst {$env:cdinst = $pwd; echo "cdinst=$pwd"}
function mksrc {$env:cdsrc = $pwd; echo "cdsrc=$pwd"}
function mktest {$env:cdtest = $pwd; echo "cdtest=$pwd"}
function cdinst {echo "cd \"$env:cdinst\""; & cd $env:cdinst}
function cdsrc {echo "cd \"$env:cdsrc\""; & cd $env:cdsrc}
function cdtest {echo "cd \"$env:cdtest\""; & cd $env:cdtest}
function scd {echo "cdinst=\"$env:cdinst\""; echo "cdisrc=\"$env:cdsrc\""; echo "cdtest=\"$env:cdtest\""}
