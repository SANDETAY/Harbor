$root = Split-Path -Parent $PSScriptRoot
$zipPath = Join-Path $root "harbor-webapp-deploy.zip"

if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

$files = @(
  "index.html",
  "manifest.webmanifest",
  "sw.js",
  "harbor-favicon-32.png",
  "harbor-apple-touch.png",
  "harbor-icon-192.png",
  "harbor-icon-512.png",
  "harbor-mark.png",
  "harbor-mark.svg",
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
