# Reversible Night and icon test on the TCL

The owner authorized a physical-TV test on 2026-11-01. The target is the
owner-reported TCL 85QM850G, 85 inches. The existing authorized ADB connection
reports Android 11, model `Smart TV Pro`, physical display surface 1920 × 1080
and density 320. These are Android's reported values; they do not establish the
panel's native resolution. No display-size or density override is applied.

## Isolation and build

`-PvisualTest=true -PiconRenderScale=2` builds an ordinary app named **Couch TV
Visual Test**, package `app.couchtv.launcher.visualtest`. Its activity is still
`app.couchtv.launcher.MainActivity`. The visual test has its own data directory
and no Android HOME intent category, so it cannot become the Home destination.
Normal builds retain the original package, label and HOME category.

The test bundles the exact reviewed 4K Night photo, transparent foreground and
glass fill, selecting them only in its generated web assets. Icon rendering is
2x. The original web source files and original background assets are unchanged.
It runs the bundled page without a bridge, skips the Watch Next permission
request, and offers no upstream app updates. The private test configuration
selects only Night and excludes smart-home credentials. Nothing is published
from that configuration, device connection record, screenshots or APK backup.

The current Home app and its settings stay installed. The Synology bridge,
launcher preference, system packages, Wi-Fi, display settings and debugging
authorization are not changed. The new test app may appear in the normal list
of installed apps until it is removed.

Build with the existing local JDK/SDK environment and a private test configuration:

```sh
build/gradle-8.11.1/bin/gradle -p tv-home/android :app:testDebugUnitTest :app:assembleDebug -PvisualTest=true -PiconRenderScale=2 -PconfigJson=<absolute-path-to-private-test-config>
```

Before installation, verify the APK package, label, activity and absence of the
HOME category. Verify its bundled Night files match the candidate checksums.
Back up the currently installed Home APK to the ignored build directory. Never
use `apply.sh` for this isolated test: no launcher takeover is needed.

## Run and roll back

After the user confirms they are at the TV, install the test APK with the
repository's pure-Python `tvadb.py`, then explicitly launch:

```sh
TV_IP=<tv-address> .venv/bin/python tv-home/tools/tvadb.py shell 'am start -W -n app.couchtv.launcher.visualtest/app.couchtv.launcher.MainActivity --es bridge none'
```

**Press Home on the TV remote to return to the working dashboard.** This is the
normal rollback; the existing launcher was never replaced. Reopen Couch TV
Visual Test from the app list to compare again. To stop the test from this
computer, send Home then force-stop only the test package:

```sh
TV_IP=<tv-address> .venv/bin/python tv-home/tools/tvadb.py keys HOME
TV_IP=<tv-address> .venv/bin/python tv-home/tools/tvadb.py shell 'am force-stop app.couchtv.launcher.visualtest'
```

Removing the experiment later means uninstalling only **Couch TV Visual Test**,
not the existing **Home** app. The backed-up Home APK is an additional precaution;
reinstalling it is unnecessary for the normal rollback. The private local control
script and backup live in ignored `build/night-4k/`.

## Acceptance

Check the clock/mountain boundary, actual installed-app icons, focus movement,
opening an app, and returning to the original dashboard with Home. Capture
the visible result and check for crashes. Record actual results below; desktop
previews alone do not verify these behaviors. With the reported 1080p Android
surface, sharper 4K presentation is not guaranteed. This first test does not
change the device's rendering resolution or qualify long-run memory/performance.

## Observed results — 2026-11-01

- The isolated APK compiled; all eight existing Android unit tests passed.
- APK inspection verified its separate package/label, absence of the HOME
  category, and exact inclusion/selection of all three reviewed 4K Night assets.
- The installed original Home APK was backed up under ignored `build/night-4k/`.
- Side-by-side installation succeeded. Explicit launch reported a 1600 ms cold
  activity start; this is Android's activity timing, not time to a fully painted
  scene. An initial screenshot was still loading; a later capture showed the
  complete Night scene, clock behind the mountain, and actual installed-app dock.
- One cached native test banner was read back and decoded at 1280 × 720.
- Remote left/right inputs were sent, and selecting the focused YouTube icon
  opened the installed YouTube app.
- Sending Home returned to `app.couchtv.launcher/.MainActivity`. The original
  package remained the resolved Home activity. The test was force-stopped and
  then reopened for the owner's visual inspection.
- The captured test-app log contained no `FATAL EXCEPTION`. One early process
  sample reported approximately 76 MiB total PSS; this single sample does not
  establish settled memory consumption or long-run stability.
- A default build also compiled and its generated values were checked:
  original application ID, `VISUAL_TEST=false`, `ICON_RENDER_SCALE=1`.

The owner confirmed: **“Looks right and navigation feels normal.”** This accepts
the visible test and basic navigation, not a measured sharpness improvement or
extended performance qualification. No true-4K
Android rendering, reboot/standby testing, bridge integration in the test app,
or final acceptance is claimed. Private screenshot and logs remain local.
