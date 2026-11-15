# Upstream main integration

**Goal:** Merge upstream `844b4df2fa8386b4caa419a77267e3803456763e` into the fork at `93fcb89`, retaining Synology and launcher customizations, then commit and push the task branch.

**Architecture:** Keep upstream history through a merge. Resolve overlapping launcher changes explicitly, retaining the fork's server loading deadline, foreground recovery, validated offline cache, persistent weather, native Continue Watching fallback, update source and cinematic remote artwork. Keep the hardened root Docker setup alongside upstream's separate Docker example.

**Constraints:** Repository integration only; no TV or NAS deployment. Do not include personal configuration, keys, data or build products. Use synthetic unpaired TVs and public example settings for validation. Preserve the existing private signing identity without printing or committing it.

- [x] Resolve five conflicting files and inspect automatic merges against both parents.
- [x] Exercise native Continue Watching fallback together with upstream removal, exclusions and toggle; cached weather together with ambient weather; local loading together with WebView recovery and restart.
- [x] Include the new bridge web helper in the Synology image; verify non-root/read-only runtime, configuration seeding, persistent identity and new routes using an isolated local container.
- [x] Run applicable Python, Node, browser, shell, remote build and Android unit/release checks; compare failures against pristine upstream when necessary.
- [x] Review the final diff and privacy scan, record verification and limitations, and prepare `codex/upstream-main-integration-2026-11-14` for commit, push and remote SHA verification.

## Review focus

- Missing Wi-Fi must not delay the local home behind upstream's network wait.
- Server recovery must not reload the page during navigation or playback.
- Upstream WebView failure handling and pairing-key propagation must survive the merge.
- Native fallback must respect upstream hidden shows, excluded packages and Keep watching off.
- Weather must feed ambient effects while expiring stale or mismatched-place readings.
- Image rebuilds must preserve the existing volume layout, non-root identity, key and configuration.

## Verification

- 782 Python cases across 50 modules passed in isolated subprocesses after adapting the fork's pairing guard to Android only and preserving upstream error-message keys. The three initially failing modules were rerun successfully (power-on, Philips SAPHI and translated bridge messages).
- 10 rendered preview cases, 3 browser home cases, 4 served mobile/platform asset cases and 1 container identity case passed: 800 Python cases total. A visual-preview timeout did not reproduce when isolated or on the complete repeat; an incomplete ambient-weather spy was replaced with instrumentation of the real engine.
- 14 Node checks passed, including the fork's weather-cache policy. Remote production build passed.
- Launcher: 21 JVM tests; on-TV app: 52 JVM tests; all passed. Launcher, on-TV and experimental sync release builds passed; all three APK signatures verified. Bundled configuration was the public example; no APK was installed. Builds use the existing local test signing configuration, not a newly generated production release identity.
- Linux/amd64 Synology image built successfully. The disposable container ran as UID/GID 10001 with a read-only filesystem, dropped capabilities, loopback-only publication and retained test volumes. ADB key fingerprints survived restart. Both cinematic and legacy mobile icon URLs returned the expected PNG bytes, with revalidation headers. HTML, manifest, onboarding bundle and `/bridge/shim.js` were checked. `/titan/` and `/vidaa/icon.png` were checked after the review found they needed packaging.
- The new CI job builds this root image and checks icon delivery and persistent identity against synthetic unpaired settings. Existing CI retains both Android unit-test suites.
- Python/shell/JavaScript syntax and workflow YAML parse checks passed. Two upstream whitespace issues were normalized. Source-only privacy scan on an export containing only tracked/task source passed with zero findings, including Gitleaks 8.30.1. Image metadata inspection was skipped because exiftool is unavailable; Git history was outside that source-only scan. Two old `@2x.jpg` URL strings were URL-encoded to avoid false email detections.
- Latest upstream ref was rechecked and remained `844b4df2fa8386b4caa419a77267e3803456763e`.

## Review and limits

An independent read-only reviewer checked loading/recovery, authentication propagation, native history filtering, ambient weather and artwork delivery. Its only important finding was the omitted Titan/TiVo page and VIDAA icon in the root image; those assets were added and their endpoints tested.

Known inherited limitations remain: offline WebView renderer recovery can leave the local view absent, and LAN metadata injection can disagree with the offline manifest's index byte count. Neither was introduced by this merge. No NAS or TV deployment, pairing, package changes or physical-device validation occurred. Existing mobile Home Screen bookmarks may retain their OS-cached image until refreshed or added again; the server now serves the cinematic art on both old and new icon URLs.

Delivery branch: `codex/upstream-main-integration-2026-11-14`. The completion report records the delivered commit and remote SHA verification.
