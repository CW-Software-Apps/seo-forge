<#
.SYNOPSIS
    SEO-FORGE: Quick Auto-Updater Script
    CW Software (https://cwsoftware.com.br)

.EXAMPLE
    .\update.ps1
    irm https://raw.githubusercontent.com/CW-Software-Apps/seo-forge/main/update.ps1 | iex
#>

[CmdletBinding()]
param(
    [string]$TargetDir = (Get-Location).Path
)

$localInstall = if (![string]::IsNullOrEmpty($PSScriptRoot)) { Join-Path $PSScriptRoot "install.ps1" } else { $null }

if ($localInstall -and (Test-Path $localInstall)) {
    & $localInstall -Update -TargetDir $TargetDir
} else {
    $scriptUrl = "https://raw.githubusercontent.com/CW-Software-Apps/seo-forge/main/install.ps1"
    $code = Invoke-RestMethod -Uri $scriptUrl
    Invoke-Expression "& { $code } -Update -TargetDir '$TargetDir'"
}
