# 60 saniyelik demo: her adımı yazar, çalıştırır, Enter bekler.
$exe = Join-Path $PSScriptRoot '.venv\Scripts\gpower-clone.exe'

function Step($title, [string[]]$cliArgs) {
    Write-Host ""
    Write-Host "== $title" -ForegroundColor Cyan
    Write-Host ("> gpower-clone " + ($cliArgs -join ' ')) -ForegroundColor Yellow
    & $exe @cliArgs
    Write-Host "(cikis kodu: $LASTEXITCODE)" -ForegroundColor DarkGray
    Read-Host "Devam icin Enter" | Out-Null
}

Clear-Host
Step '1) A priori: gereken orneklem buyuklugu' @('--test','chi2-contingency','--mode','a-priori','--w','0.3','--alpha','0.05','--power','0.95','--df','5')
Step '2) Post hoc: ulasilan guc' @('--test','chi2-contingency','--mode','post-hoc','--w','0.3','--alpha','0.05','--n_total','100','--df','5')
Step '3) Gecersiz girdi: w = 0' @('--test','chi2-contingency','--mode','a-priori','--w','0','--alpha','0.05','--power','0.8','--df','1')

Write-Host ""
Write-Host "== 4) Uyum raporu (tests/REPORT.md)" -ForegroundColor Cyan
Get-Content (Join-Path $PSScriptRoot 'tests\REPORT.md') -Encoding UTF8 -TotalCount 6
