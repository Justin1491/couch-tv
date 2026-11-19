const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const activity = fs.readFileSync(path.join(__dirname,
  "../tv-home/android/app/src/main/java/app/couchtv/launcher/MainActivity.kt"), "utf8");
const probe = activity.match(/RECOVERY_PAGE_READY = """([\s\S]+?)"""/);
assert.ok(probe, "the launcher has a readiness probe for the recovered bridge page");

function ready({ night = true, settled = false, tiles = 0, photo = null } = {}) {
  return vm.runInNewContext(probe[1], {
    window: { tv: {} },
    performance: { getEntriesByName: () => settled ? [{}] : [] },
    document: {
      getElementById: () => ({ childElementCount: tiles }),
      documentElement: { classList: { contains: () => night } },
      querySelector: () => photo,
    },
  });
}

assert.equal(ready(), false, "the static Keep watching title is an unfinished Home");
assert.equal(ready({ tiles: 3, photo: { complete: true, naturalWidth: 1920 } }), false,
  "a page that has not finished synchronizing must stay hidden");
assert.equal(ready({ settled: true, tiles: 3 }), false,
  "the Night layout must have a scene before being shown");
assert.equal(ready({ settled: true, tiles: 3, photo: { complete: true, naturalWidth: 0 } }), false,
  "an image load failure cannot reveal a black scene");
assert.equal(ready({ settled: true, tiles: 3, photo: { complete: true, naturalWidth: 1920 } }), true);
assert.equal(ready({ settled: true, tiles: 3, night: false }), true,
  "other layouts can finish without a Night scene");
