# Harbor local preview server — always use this (never double-click HTML files).
# Usage:  npm start
#    or:  powershell -ExecutionPolicy Bypass -File scripts/start-server.ps1
#    or:  double-click preview.cmd in the Harbor folder

$ErrorActionPreference = "Stop"
$port = 3000
$root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $root "index.html"))) {
  Write-Host "ERROR: index.html not found in $root" -ForegroundColor Red
  exit 1
}

function Test-PortFree([int]$p) {
  try {
    $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    return -not $c
  } catch {
    return $true
  }
}

# Pick a free port (3000–3010)
$chosen = $null
foreach ($p in 3000..3010) {
  if (Test-PortFree $p) { $chosen = $p; break }
}
if (-not $chosen) {
  Write-Host "ERROR: Ports 3000-3010 are all in use. Close other servers and retry." -ForegroundColor Red
  exit 1
}
$port = $chosen

$dual = "http://127.0.0.1:$port/dual-preview.html"
$web  = "http://127.0.0.1:$port/index.html"
$mob  = "http://127.0.0.1:$port/mobile.html"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Harbor local preview server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Folder: $root"
Write-Host ""
Write-Host "  Dual (web + phone):  $dual" -ForegroundColor Green
Write-Host "  Web only:            $web"
Write-Host "  Mobile only:         $mob"
Write-Host ""
Write-Host "  Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Open dual preview after a short delay so the server is listening
$openScript = @"
Start-Sleep -Seconds 0.8
try { Start-Process '$dual' } catch {}
"@
Start-Process powershell -ArgumentList "-NoProfile -WindowStyle Hidden -Command $openScript" -WindowStyle Hidden

Set-Location $root

# Prefer Python ThreadingHTTPServer (handles concurrent iframe loads)
$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if (-not $py) {
  Write-Host "ERROR: Python not found (py/python). Install Python or run: npx serve -l $port" -ForegroundColor Red
  exit 1
}

# Inline server so two iframes can load index.html at once without freezing
$code = @"
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import sys
port = int(sys.argv[1])
class H(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
        '.html': 'text/html; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.json': 'application/json; charset=utf-8',
        '.svg': 'image/svg+xml',
        '.webmanifest': 'application/manifest+json'}
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()
    def log_message(self, fmt, *args):
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))
ThreadingHTTPServer.allow_reuse_address = True
httpd = ThreadingHTTPServer(('127.0.0.1', port), H)
print('Serving Harbor on http://127.0.0.1:%d/' % port, flush=True)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    httpd.server_close()
"@

& $py.Source -c $code $port
