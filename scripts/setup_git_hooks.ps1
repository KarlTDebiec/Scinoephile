#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$projectRoot = Join-Path $scriptDir ".." | Resolve-Path | Select-Object -ExpandProperty Path
$hooksSrc = Join-Path $projectRoot "scripts/git_hooks"
$hooksDest = Join-Path $projectRoot ".git/hooks"

Get-ChildItem $hooksSrc | ForEach-Object {
    $dest = Join-Path $hooksDest $_.Name
    Copy-Item $_.FullName $dest -Force
    Write-Host "Installed $($_.Name)" 1>&2
}
