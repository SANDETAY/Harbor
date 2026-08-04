# Prepare web assets for Capacitor (copies PWA files into native-www/)
# Run from repo root: powershell -ExecutionPolicy Bypass -File scripts/cap-prepare.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$out = Join-Path $root "native-www"
if (Test-Path $out) {
  Remove-Item -Recurse -Force $out
}
New-Item -ItemType Directory -Path $out | Out-Null

$files = @(
  "index.html",
  "sw.js",
  "manifest.webmanifest",
  "privacy.html",
  "harbor-favicon-32.png",
  "harbor-apple-touch.png",
  "harbor-icon-192.png",
  "harbor-icon-512.png",
  "harbor-mark.png",
  "harbor-mark.svg",
  "harbor-splash-anchor.png",
  "harbor-splash-anchor-512.png",
  "harbor-fab-anchor.png",
  "harbor-fab-anchor-128.png"
)

foreach ($f in $files) {
  $src = Join-Path $root $f
  if (Test-Path $src) {
    Copy-Item $src (Join-Path $out $f) -Force
  } else {
    Write-Warning "Missing optional asset: $f"
  }
}

New-Item -ItemType Directory -Path (Join-Path $out "js") -Force | Out-Null
$cloudJs = Join-Path $root "js\harbor-cloud.js"
if (Test-Path $cloudJs) {
  Copy-Item $cloudJs (Join-Path $out "js\harbor-cloud.js") -Force
}
$pdfjs = Join-Path $root "js\pdfjs"
if (Test-Path $pdfjs) {
  New-Item -ItemType Directory -Path (Join-Path $out "js\pdfjs") -Force | Out-Null
  Copy-Item (Join-Path $pdfjs "*") (Join-Path $out "js\pdfjs") -Force -Recurse
  Write-Host "Included js/pdfjs (recipe PDF reader)."
}

$cfg = Join-Path $root "docs\supabase\config.local.js"
if (Test-Path $cfg) {
  New-Item -ItemType Directory -Path (Join-Path $out "docs\supabase") -Force | Out-Null
  Copy-Item $cfg (Join-Path $out "docs\supabase\config.local.js") -Force
  Write-Host "Included docs/supabase/config.local.js in native-www."
} else {
  Write-Warning "docs/supabase/config.local.js missing - cloud sign-in will stay unconfigured in native shell."
}

if (-not (Test-Path (Join-Path $out "index.html"))) {
  throw "index.html missing - cannot prepare Capacitor webDir"
}

Write-Host "Prepared $out for Capacitor (webDir)."
Write-Host "Next: npx cap sync ios   (then on a Mac: cd ios/App ; pod install ; npx cap open ios)"
Write-Host "App Store runbook: docs/APP-STORE-IOS.md"
