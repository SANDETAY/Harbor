$port = 3000
$root = Split-Path -Parent $PSScriptRoot

Write-Host "Harbor previews:"
Write-Host "  Web     http://localhost:$port/index.html"
Write-Host "  Mobile  http://localhost:$port/mobile.html"
Write-Host "  Dual    http://localhost:$port/dual-preview.html"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

Push-Location $root
try {
  py -m http.server $port
} finally {
  Pop-Location
}