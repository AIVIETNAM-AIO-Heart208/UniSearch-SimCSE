# Builds build/main.pdf with pdfLaTeX + BibTeX, without latexmk (MiKTeX's latexmk needs Perl).
# Usage (from the repo root):  powershell -ExecutionPolicy Bypass -File docs\report\build.ps1 [-Clean]
param([switch]$Clean)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

if ($Clean -and (Test-Path build)) { Remove-Item -Recurse -Force build }
New-Item -ItemType Directory -Force build | Out-Null

function Invoke-Tool([string]$Exe, [string[]]$ToolArgs) {
    & $Exe @ToolArgs | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "$Exe failed (exit $LASTEXITCODE). See docs/report/build/main.log or main.blg."
    }
}

$pdflatexArgs = @('-interaction=nonstopmode', '-halt-on-error', '-file-line-error',
                  '-output-directory=build', 'main.tex')
Invoke-Tool 'pdflatex' $pdflatexArgs
Invoke-Tool 'bibtex' @('build/main')
Invoke-Tool 'pdflatex' $pdflatexArgs
Invoke-Tool 'pdflatex' $pdflatexArgs

# Surface what still needs attention instead of hiding it in the log.
$warnings = @(Select-String -Path build/main.log -Pattern 'Warning|Overfull') +
            @(Select-String -Path build/main.blg -Pattern '^Warning--') | ForEach-Object { $_.Line.Trim() }
$todos = Select-String -Path main.tex, sections/*.tex -Pattern '\\TODO\{'
Write-Output "PDF: $(Join-Path $PSScriptRoot 'build\main.pdf')"
Write-Output "LaTeX/BibTeX warnings and overfull boxes: $(@($warnings).Count)"
$warnings | Select-Object -First 20 | ForEach-Object { Write-Output "  $_" }
Write-Output "TODO notes left: $(@($todos).Count) (all must be removed before submission)"
