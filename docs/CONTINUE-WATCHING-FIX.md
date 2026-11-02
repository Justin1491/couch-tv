# Continue Watching after the visual test

Investigation on 2026-11-01 confirmed the owner was using the original Home
package, not the separate visual-test app. An earlier physical-TV screenshot
showed Continue Watching entries. The current screenshot showed no row.
The Synology bridge was healthy, paired and connected with ADB available, but
its history endpoint and Continue Watching endpoint both returned zero items.
No viewing titles, credentials or private screenshots are included here.

The web page reads Android's native Watch Next list in local mode. In connected
mode it used only `/api/continue`. A successful empty bridge response therefore
cleared the visible row even if the TV had its own entries. This is a mismatch
between the two modes; the diagnostics do not establish that the visual test
deleted any viewing history.

The fix retains nonempty bridge results, but falls back to the TV's native list
when the bridge responds with no entries. Native items remain shared across
viewers, as they already were in local mode. They stay on the TV; the fallback
does not upload them to the bridge. An unavailable/malformed native list safely
returns no entries. This does not import streaming-account histories or invent
new viewing records.

Regression validation: the connected/empty-bridge test failed before the fix,
then passed afterward. A nonempty bridge list remains preferred. All six
browser checks in `tests/test_night_4k_preview.py` passed after the change.

The corrected bridge image must be deployed to update the connected page. Keep
the previous image and the existing configuration/data volumes. Do not delete
or reset volumes, rerun pairing, or replace the TV's working Home APK for this
web-only correction. Confirm the row on the actual TV after deployment before
claiming the live issue is fixed.

## Deployment verification

The owner opened the signed-in DSM Container Manager session. The corrected
`couch-tv-bridge:continue-fix` image was imported alongside the existing image.
The project's YAML was preserved and checked: only the image tag changed;
configuration/data volumes and network settings were retained. The bridge
project was recreated, with pairing, TV connection and ADB still healthy.
The served `app.js` matched the locally tested file byte-for-byte.

The existing Home app was reloaded without changing its settings or APK.
A physical-TV capture confirmed the Continue Watching row returned with native
TV entries in Classic layout. The owner subsequently navigated the look settings;
no further remote inputs were sent. The bridge history remains empty; this
verifies the fallback rather than claiming a history import. Private captures
remain in the ignored build folder.

The previous `couch-tv-bridge:local` image remains available: restoring that tag
and recreating the project with the same volumes rolls back this web correction.
