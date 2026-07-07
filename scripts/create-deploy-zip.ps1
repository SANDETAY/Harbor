$root = Split-Path -Parent $PSScriptRoot
$zipPath = Join-Path $root "rhythm-webapp-deploy.zip"

if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

$files = @(
  "index.html",
  "manifest.webmanifest",
  "sw.js",
  "rythm-r-mark.png",
  "rythm-wordmark.png",
  "netlify.toml"
)

Push-Location $root
try {
  Compress-Archive -Path $files -DestinationPath $zipPath -Force
  Write-Host "Created: $zipPath"
  Write-Host "Drag this zip to https://app.netlify.com/drop to deploy."
} finally {
  Pop-Location
}