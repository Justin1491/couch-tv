const test = require('node:test');
const assert = require('node:assert/strict');
const cache = require('../tv-home/web/weather-cache.js');

test('weather survives restart, but expires after two hours', () => {
  const place = { lat: 40, lon: -74, timezone: 'America/New_York' };
  const record = cache.record(place, { temp: 18, code: 0, is_day: true }, 1000);
  assert.equal(cache.read(record, place, 1001).temp, 18);
  assert.equal(cache.read(record, place, 1000 + 2 * 60 * 60 * 1000), null);
});

test('a cached reading never crosses locations', () => {
  const place = { lat: 40, lon: -74 };
  const record = cache.record(place, { temp: 18, code: 0 }, 1000);
  assert.equal(cache.read(record, { lat: 41, lon: -74 }, 1001), null);
});

test('future timestamps, malformed records and invalid readings are rejected', () => {
  const place = { lat: 40, lon: -74 };
  assert.equal(cache.read(null, place, 1000), null);
  assert.equal(cache.record(place, { temp: NaN, code: 0 }, 1000), null);
  assert.equal(cache.record(place, { temp: null, code: 0 }, 1000), null);
  assert.equal(cache.read(cache.record(place, { temp: 18, code: 0 }, 2000), place, 1000), null);
});
