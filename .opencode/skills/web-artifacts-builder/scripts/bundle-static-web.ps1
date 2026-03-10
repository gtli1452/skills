[CmdletBinding()]
param(
    [string]$EntryPoint = 'index.html',
    [string]$OutputFile = 'bundle.html',

    [ValidateSet('auto', 'pnpm', 'npm')]
    [string]$PackageManager = 'auto'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-PackageManager {
    param([string]$Requested)

    if ($Requested -ne 'auto') {
        return $Requested
    }

    if (Get-Command pnpm -ErrorAction SilentlyContinue) {
        return 'pnpm'
    }

    return 'npm'
}

    function Install-BundleDependencies {
        param([string]$Manager)

        $packages = @('parcel', '@parcel/config-default', 'parcel-resolver-tspaths', 'html-inline')
        if ($Manager -eq 'pnpm') {
            $args = @('add', '-D') + $packages
            & pnpm @args
        }
        else {
            $args = @('install', '-D') + $packages
            & npm @args
        }
    }

function Format-Size {
    param([long]$Bytes)

    if ($Bytes -ge 1MB) {
        return ('{0:N2} MB' -f ($Bytes / 1MB))
    }
    if ($Bytes -ge 1KB) {
        return ('{0:N2} KB' -f ($Bytes / 1KB))
    }
    return "$Bytes B"
}

if (-not (Test-Path -LiteralPath 'package.json')) {
    throw 'No package.json found. Run this script from the project root.'
}
if (-not (Test-Path -LiteralPath $EntryPoint)) {
    throw "Entry point not found: $EntryPoint"
}

$resolvedManager = Get-PackageManager -Requested $PackageManager
Write-Host "Using package manager: $resolvedManager"

Install-BundleDependencies -Manager $resolvedManager

if (-not (Test-Path -LiteralPath '.parcelrc')) {
    Set-Content -LiteralPath '.parcelrc' -Encoding UTF8 -Value @'
{
  "extends": "@parcel/config-default",
  "resolvers": ["parcel-resolver-tspaths", "..."]
}
'@
}

Remove-Item -LiteralPath 'dist' -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $OutputFile -Force -ErrorAction SilentlyContinue

if ($resolvedManager -eq 'pnpm') {
    & pnpm exec parcel build $EntryPoint --dist-dir dist --no-source-maps
    & pnpm exec html-inline 'dist/index.html' | Set-Content -LiteralPath $OutputFile -Encoding UTF8
}
else {
    & npx parcel build $EntryPoint --dist-dir dist --no-source-maps
    & npx html-inline 'dist/index.html' | Set-Content -LiteralPath $OutputFile -Encoding UTF8
}

$bundle = Get-Item -LiteralPath $OutputFile
Write-Host ''
Write-Host "Bundle complete: $($bundle.FullName) ($(Format-Size -Bytes $bundle.Length))"
Write-Host 'Open the bundle in a local browser or attach it to any static hosting flow.'
