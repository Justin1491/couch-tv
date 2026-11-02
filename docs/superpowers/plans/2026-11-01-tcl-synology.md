# TCL and Synology Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Prepare and deploy a server-first couch-tv home with quiet local fallback and a Synology bridge.

**Architecture:** Keep the existing Kotlin/WebView launcher and web interface. Bound server loading, preserve local assets and direct app launching, and containerize the existing Python bridge and phone frontend.

**Tech Stack:** Kotlin, Android SDK 34, JavaScript, Node, Python 3.11, Docker Compose.

**Spec:** ../specs/2026-11-01-tcl-synology-design.md

## Global Constraints

- Server-first with an approximately one-second initial loading budget.
- Quiet offline operation and no automatic recovery reload during navigation.
- No personal configuration, pairing data, images or signing keys committed.
- No default-branch merge; push focused task commits to the existing fork.
- Preserve stock Home until installation and rollback details are reviewed with the user.

## Review Focus

- A delayed server callback must not replace an already-visible local home.
- Recovery while another app is playing must not interrupt playback.
- A partial asset download must preserve the last complete offline copy.
- Weather caches must not show another location's readings or indefinitely stale data.
- Container restarts must preserve pairing and avoid publishing private configuration in the image.

### Task 1: Bounded launcher loading

**Files:** MainActivity.kt; new HomeLoadPolicy.kt and HomeLoadPolicyTest.kt under the Android app; app/build.gradle.kts.

**Interfaces:** HomeLoadPolicy owns attempt generations, a 1000 ms budget, capped retry delays and a recovered bridge address. MainActivity owns WebView and Android lifecycle effects.

- [ ] Write and run failing JVM tests for timeout versus late completion, recovery deferred to Home, and retry reset/capping.
- [ ] Integrate the policy into startup, callbacks, background probing and Home transitions; keep direct app launch unchanged.
- [ ] Preserve the previous complete asset directory when switching downloaded copies.
- [ ] Run JVM tests and build the release APK with a persistent private signing key and fork update target.

### Task 2: Quiet web home and weather

**Files:** tv-home/web/app.js; new weather-cache.js; index.html; tests/weather-cache.test.cjs; browser integration tests under tests/.

**Interfaces:** Weather cache keys include location and store acceptance time; visible readings expire after two hours. Existing Settings/About retains connection status.

- [ ] Write and run failing weather tests for location separation, expiry and invalid/future readings.
- [ ] Fetch weather independently with a bounded timeout, preserve last-good readings, and suppress persistent bridge outage messages on Home.
- [ ] Test the rendered offline home, app launching, settings status and failed weather refresh in a browser.

### Task 3: Synology deployment

**Files:** Dockerfile; .dockerignore; compose.yaml; docs/SYNOLOGY.md; tests/test_container.py; deployment configuration stays ignored.

**Interfaces:** /config/config.json is writable for pairing; /data persists bridge state; port 5400 serves API, TV home and built phone frontend.

- [ ] Build the frontend in a Node stage and run the Python bridge as a non-root user with health checks and restart policy.
- [ ] Validate Compose and build/run the image; verify health, TV assets and phone frontend, then restart and confirm persistence.
- [ ] Document pairing, LAN restriction, startup and rollback; deploy only after identifying NAS access and existing services.

### Task 4: Device acceptance and delivery

- [ ] Discover TCL, verify debugging support, collect weather/app preferences and review exact device changes before installing.
- [ ] Pair bridge and launcher, then verify Home and two apps with the user.
- [ ] Exercise bridge stopped, unreachable and restored; record actual startup times and residual gaps.
- [ ] Review changes, run privacy scan, commit, push and verify the remote branch.
