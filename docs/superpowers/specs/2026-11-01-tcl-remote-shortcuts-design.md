# TCL app-button repair

Status: TV-based approach selected; design awaiting approval. No implementation or installation yet.

## Goal and device evidence

Make the physical remote's app buttons open their apps from couch-tv and from
other apps, while Home continues to open couch-tv. The repair should run on the
TV and continue working without the NAS or network.

On the tested TCL running Android 11, the physical app-button signals reach the
input subsystem. Disabling the whole Google TV Home package removes its
`com.google.global_button.ACTION_LAUNCH_APP` receiver. Temporarily re-enabling
that package restored the shortcuts, but Home opened Google TV. The firmware
rejected disabling its HomeActivity separately. The original couch-tv setup was
restored afterward. These observations do not establish that an accessibility
service will receive the vendor shortcut events.

## Approaches

- **TV-based button handler (selected):** add an optional AccessibilityService to
  the existing couch-tv Home app. Android provides key filtering before device
  policy and applications. This needs one explicit accessibility permission and
  real-device proof that TCL supplies the necessary events.
- **NAS input listener:** read remote presses through ADB and launch apps from the
  bridge. This adds network latency and depends on NAS availability, so it is a
  fallback to consider only if the TV-based approach fails and the user chooses it.
- **Keep Google's shortcut handler:** already tested. Enabling its package also
  restores Google's Home behavior; this TV refuses the narrower component change.

The user selected the TV-based prototype. The implementation details below are
proposed engineering choices, not previously approved device changes.

## Proposed behavior

Add the service to the existing `app.couchtv.launcher` APK, off until explicitly
enabled. Keep the Google TV package disabled. Do not alter the NAS or its daily
keep-disabled list for this approach.

First build a bounded calibration mode that identifies one named app button at
a time and associates it with an installed TV app. Use the Android key and scan
codes actually observed, rather than guessing from the Linux event labels.
Reject ordinary navigation, Home, Back, power, volume, playback, and printable
keys. Store only the selected remote-button identifiers and app mappings in
private on-TV preferences; do not log or retain the general key stream.

Once a mapped press is recognized, consume its matching down/up sequence and
open the app once. Holding a button must not launch it repeatedly. Unmapped
buttons pass through normally. If a target app is absent or cannot launch, do
not open a store, change the mapping, or repeatedly retry. Include a clear
local status and an option to turn the handler off and clear its mappings.

The service requests key filtering only: no screen-content retrieval,
screenshots, touch exploration, or network communication for button handling.
Do not turn off or replace another accessibility service to gain key access.
A conflicting service or unavailable key events must be reported as a limit.

## Verification and rollout

Build and test the APK locally before proposing installation. Unit checks cover
mapping exclusions, one launch per press, repeats, canceled presses, and matching
key releases. Android build checks verify the service declaration and resources.

Before any TV installation, present the exact APK update, accessibility permission,
calibration steps, and rollback, and wait for a clear yes. Preserve the previous
signed APK. Do not enable the service through secure-settings writes or grant
additional privileges without a separate, explicit explanation and approval.

First prove event delivery on the TCL. If the service cannot see the shortcut
buttons, stop the experiment and explain the result; do not change Google TV,
install another remapper, or add a NAS workaround automatically.

If delivery works, verify Netflix and another mapped app from Home and from a
different running app. Check Home, Back, navigation, volume, playback, and TCL's
own button; test held buttons, standby, restart, and operation with NAS unavailable.
A successful build alone is not evidence of repaired physical buttons.

## Undo

Turn off the couch-tv button handler in the TV's Accessibility settings. That
immediately returns key handling to the current setup. Clear mappings if wanted;
reinstall the previous signed APK if the update itself needs rolling back. Home,
app logins, and the NAS configuration remain as before this experiment.

## Reference and unresolved proof

Android documents the early key callback here:
https://developer.android.com/reference/android/accessibilityservice/AccessibilityService#onKeyEvent(android.view.KeyEvent)

The decisive unknown is whether this TCL firmware delivers its vendor app-button
events to that callback. Real-device calibration is the acceptance gate.
