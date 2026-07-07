# Install a winget package to P:\Program Files by default.
# Usage: .\Install-ToP.ps1 Git.Git
#        .\Install-ToP.ps1 Microsoft.VisualStudioCode

param(
    [Parameter(Mandatory = $true)]
    [string]$PackageId,

    [string]$Location = "P:\Program Files"
)

$folderName = ($PackageId -split '\.')[-1]
$target = Join-Path $Location $folderName
Write-Host "Installing $PackageId to $target ..."
winget install --id $PackageId -e --location $target --accept-source-agreements --accept-package-agreements