#
# Powershell initilization script
#
# . c:\software\etc\setbin.ps1
#
$env:PYTHON3 = $env:SOFTWAREDIR + "\bin\python.bat"

$env:SOFTWAREDIR=(Split-Path (Split-Path $MyInvocation.MyCommand.Path))
$env:PATH = $env:SOFTWAREDIR + "\bin;" + $env:PATH
echo "Prefixed PATH with ""$env:SOFTWAREDIR\bin""."

# cd[a-z], mk[a-z]
function mka { $env:cda = $pwd; echo "cda=$pwd" }
function cda { echo "cd \"$env:cda\""; & cd $env:cda }
function mkb { $env:cdb = $pwd; echo "cdb=$pwd" }
function cdb { echo "cd \"$env:cdb\""; & cd $env:cdb }
function mkc { $env:cdc = $pwd; echo "cdc=$pwd" }
function cdc { echo "cd \"$env:cdc\""; & cd $env:cdc }
function mkd { $env:cdd = $pwd; echo "cdd=$pwd" }
function cdd { echo "cd \"$env:cdd\""; & cd $env:cdd }
function mke { $env:cde = $pwd; echo "cde=$pwd" }
function cde { echo "cd \"$env:cde\""; & cd $env:cde }
function mkf { $env:cdf = $pwd; echo "cdf=$pwd" }
function cdf { echo "cd \"$env:cdf\""; & cd $env:cdf }
function mkg { $env:cdg = $pwd; echo "cdg=$pwd" }
function cdg { echo "cd \"$env:cdg\""; & cd $env:cdg }
function mkh { $env:cdh = $pwd; echo "cdh=$pwd" }
function cdh { echo "cd \"$env:cdh\""; & cd $env:cdh }
function mki { $env:cdi = $pwd; echo "cdi=$pwd" }
function cdi { echo "cd \"$env:cdi\""; & cd $env:cdi }
function mkj { $env:cdj = $pwd; echo "cdj=$pwd" }
function cdj { echo "cd \"$env:cdj\""; & cd $env:cdj }
function mkk { $env:cdk = $pwd; echo "cdk=$pwd" }
function cdk { echo "cd \"$env:cdk\""; & cd $env:cdk }
function mkl { $env:cdl = $pwd; echo "cdl=$pwd" }
function cdl { echo "cd \"$env:cdl\""; & cd $env:cdl }
function mkm { $env:cdm = $pwd; echo "cdm=$pwd" }
function cdm { echo "cd \"$env:cdm\""; & cd $env:cdm }
function mkn { $env:cdn = $pwd; echo "cdn=$pwd" }
function cdn { echo "cd \"$env:cdn\""; & cd $env:cdn }
function mko { $env:cdo = $pwd; echo "cdo=$pwd" }
function cdo { echo "cd \"$env:cdo\""; & cd $env:cdo }
function mkp { $env:cdp = $pwd; echo "cdp=$pwd" }
function cdp { echo "cd \"$env:cdp\""; & cd $env:cdp }
function mkq { $env:cdq = $pwd; echo "cdq=$pwd" }
function cdq { echo "cd \"$env:cdq\""; & cd $env:cdq }
function mkr { $env:cdr = $pwd; echo "cdr=$pwd" }
function cdr { echo "cd \"$env:cdr\""; & cd $env:cdr }
function mks { $env:cds = $pwd; echo "cds=$pwd" }
function cds { echo "cd \"$env:cds\""; & cd $env:cds }
function mkt { $env:cdt = $pwd; echo "cdt=$pwd" }
function cdt { echo "cd \"$env:cdt\""; & cd $env:cdt }
function mku { $env:cdu = $pwd; echo "cdu=$pwd" }
function cdu { echo "cd \"$env:cdu\""; & cd $env:cdu }
function mkv { $env:cdv = $pwd; echo "cdv=$pwd" }
function cdv { echo "cd \"$env:cdv\""; & cd $env:cdv }
function mkw { $env:cdw = $pwd; echo "cdw=$pwd" }
function cdw { echo "cd \"$env:cdw\""; & cd $env:cdw }
function mkx { $env:cdx = $pwd; echo "cdx=$pwd" }
function cdx { echo "cd \"$env:cdx\""; & cd $env:cdx }
function mky { $env:cdy = $pwd; echo "cdy=$pwd" }
function cdy { echo "cd \"$env:cdy\""; & cd $env:cdy }
function mkz { $env:cdz = $pwd; echo "cdz=$pwd" }
function cdz { echo "cd \"$env:cdz\""; & cd $env:cdz }
