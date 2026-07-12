# Creates a Play Store release keystore + key.properties (gitignored).
# Run once from repo root:  powershell -ExecutionPolicy Bypass -File scripts\create-android-keystore.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$android = Join-Path $root "android"
$keystoreDir = Join-Path $android "keystore"
$jks = Join-Path $keystoreDir "harbor-release.jks"
$keyProps = Join-Path $android "key.properties"
$creds = Join-Path $keystoreDir "CREDENTIALS.txt"

$javaHome = $env:JAVA_HOME
if (-not $javaHome -or -not (Test-Path "$javaHome\bin\keytool.exe")) {
  $candidate = "C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot"
  if (Test-Path "$candidate\bin\keytool.exe") { $javaHome = $candidate }
}
if (-not (Test-Path "$javaHome\bin\keytool.exe")) {
  throw "keytool not found. Install JDK 17 and set JAVA_HOME."
}
$keytool = Join-Path $javaHome "bin\keytool.exe"

if (Test-Path $jks) {
  Write-Host "Keystore already exists: $jks"
  Write-Host "Delete it only if you intend to create a NEW signing key (breaks Play updates)."
  exit 0
}

New-Item -ItemType Directory -Force -Path $keystoreDir | Out-Null

# Random passwords (save CREDENTIALS.txt offline)
function New-Password([int]$len = 24) {
  $chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%"
  -join (1..$len | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
}
$storePass = New-Password 28
$keyPass = $storePass
$alias = "harbor"

Write-Host "Generating release keystore..."
& $keytool -genkeypair -v `
  -keystore $jks `
  -alias $alias `
  -keyalg RSA `
  -keysize 2048 `
  -validity 10000 `
  -storepass $storePass `
  -keypass $keyPass `
  -dname "CN=Harbor, OU=Mobile, O=Sandetay, L=Unknown, ST=Unknown, C=US"

@"
storePassword=$storePass
keyPassword=$keyPass
keyAlias=$alias
storeFile=keystore/harbor-release.jks
"@ | Set-Content -Path $keyProps -Encoding ASCII

@"
Harbor Android release signing — KEEP PRIVATE — do not commit or share
Created: $(Get-Date -Format o)

Keystore file: $jks
Alias:         $alias
Store password: $storePass
Key password:   $keyPass

Back up this file + the .jks to a password manager / offline drive.
Losing them means you cannot update the same app on Google Play.
"@ | Set-Content -Path $creds -Encoding UTF8

Write-Host ""
Write-Host "Created:"
Write-Host "  $jks"
Write-Host "  $keyProps"
Write-Host "  $creds"
Write-Host ""
Write-Host "NEXT: Back up CREDENTIALS.txt, then:"
Write-Host "  cd android; .\\gradlew.bat bundleRelease"
Write-Host "See docs/PLAY-BETA.md for Play Console steps."
