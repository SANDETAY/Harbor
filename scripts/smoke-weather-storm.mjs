/**
 * Smoke: thunderstorm risk helpers + WMO mapping stay wired.
 * Run: node scripts/smoke-weather-storm.mjs
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

assert.ok(html.includes('function getHourStormRisk'), 'getHourStormRisk');
assert.ok(html.includes('function isThunderWeatherCode'), 'isThunderWeatherCode');
assert.ok(html.includes('cape'), 'CAPE in forecast payload');
assert.ok(html.includes('wind_gusts_10m'), 'gusts requested');
assert.ok(html.includes('precipitation_probability'), 'precip %');
assert.ok(html.includes('forecast_days'), 'multi-day forecast');
assert.ok(/thunderstorm/i.test(html), 'thunderstorm labels');
assert.ok(html.includes('maybeRefreshLiveWeather'), 'stale refresh');
assert.ok(html.includes('HARBOR_BUILD_NUMBER = 571'), 'build 571');

// Logic replicas
function isThunderWeatherCode(code) {
  const c = Number(code) || 0;
  return c === 95 || c === 96 || c === 99;
}

function getHourStormRisk(code, precip, precipMm, cape, gusts) {
  const c = Number(code) || 0;
  const p = Math.max(0, Number(precip) || 0);
  const mm = Math.max(0, Number(precipMm) || 0);
  const energy = Math.max(0, Number(cape) || 0);
  const g = Math.max(0, Number(gusts) || 0);
  if (isThunderWeatherCode(c)) {
    return { level: 'active', label: c >= 96 ? 'Thunder + hail' : 'Thunderstorm', score: 3 };
  }
  if (energy >= 1500 && (p >= 25 || mm >= 0.5 || (c >= 80 && c <= 82) || (c >= 61 && c <= 65))) {
    return { level: 'likely', label: 'Storm risk high', score: 2 };
  }
  if (energy >= 1000 && (p >= 35 || mm >= 1 || c >= 80)) {
    return { level: 'likely', label: 'Storm risk', score: 2 };
  }
  if (energy >= 800 && p >= 40) return { level: 'possible', label: 'Storm possible', score: 1 };
  if (energy >= 1200 && p >= 20) return { level: 'possible', label: 'Storm possible', score: 1 };
  if (g >= 45 && p >= 40 && energy >= 500) return { level: 'possible', label: 'Storm possible', score: 1 };
  return null;
}

assert.equal(getHourStormRisk(95, 10, 0, 0, 0)?.level, 'active');
assert.equal(getHourStormRisk(0, 40, 0.2, 1600, 20)?.level, 'likely');
assert.equal(getHourStormRisk(0, 10, 0, 100, 5), null);
assert.equal(getHourStormRisk(61, 50, 2, 1100, 30)?.level, 'likely');

console.log('smoke-weather-storm: ok');
