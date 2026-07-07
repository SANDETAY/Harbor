$port = 3000
$root = Split-Path -Parent $PSScriptRoot

Write-Host "Rhythm preview: http://localhost:$port"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

Push-Location $root
try {
  py -m http.server $port
} finally {
  Pop-Location
}