# TCL home screen and Synology bridge

Status: agreed direction; implementation and device installation pending.

## Intent and scope

Keep couch-tv's scenic backgrounds, clock, weather and app dock on a TCL Google
TV, with the bridge and phone remote hosted on Synology Container Manager.
Speed and quiet behavior during server outages are the priorities. Start with
the launcher and phone remote; assistant, smart-home and LG work are deferred.
Personal settings, photos, network addresses and pairing material stay out of Git.

## Approaches considered

- Unmodified bridge mode: least maintenance, but its existing timeout and outage
  messages need evaluation against the desired behavior.
- Local-first home: removes server startup dependency, but was not the user's
  preferred approach.
- Server-first with bounded local fallback: the selected direction. Retains
  server-hosted Home when available while protecting usability during outages.

## Proposed behavior

Try the server first. Use approximately one second as an initial loading budget,
measured from the launcher starting its load until the home is usable, rather
than merely until a health endpoint responds. This is a tuning target, not a
verified device result. If that budget expires, display the complete bundled or
last-good local home. Slow or stalled responses must not leave an empty screen.

Launch app shortcuts directly on the TV in both modes. Keep backgrounds, fonts,
settings and app order available locally. Downloaded home updates must preserve
the previous complete copy until the replacement is ready.

Reconnect in the background with increasing retry intervals. Show connection
details in Settings instead of persistent outage banners or repeated popups.
Defer returning to the server page until a natural Home transition; never reload
under remote navigation or interrupt a running app. The exact transition hook
is an implementation decision to verify on the device.

Weather should refresh independently of the bridge, with failed refreshes
retaining a timestamped reading temporarily and hiding it when too old. The age
limit is an implementation choice to document before release. Start with still
backgrounds and restrained transitions; adjust effects only after measuring.

## Synology and updates

Prepare a container deployment with persistent configuration and pairing data,
automatic service restart, and LAN access only. Build the phone frontend into
the container image rather than on every start. Confirm DSM, runtime support and
existing services before installation. Server outages disable phone control and
other bridge-only features; they must not disable local Home or shortcuts.

Use the personal fork as origin and the original repository as upstream. Keep
upstream main intact and work on task branches. Upstream releases do not install
automatically: review and integrate changes on a branch, resolve conflicts,
build and test, then deliberately deploy a matching TV app and bridge. Custom
builds must not offer upstream APK updates that could replace the customization
or fail due to signing differences. Retain the previous working deployment and
the custom signing key privately for rollback and future upgrades.

## Acceptance and remaining setup

Measure startup, standby recovery, navigation and direct app launching with the
bridge healthy, stopped, unreachable, slow, and failing while Home is open.
Restart the TV while the server is unavailable. Restore the bridge and verify
reconnection without focus changes, reload loops or playback interruptions.
Confirm local assets, settings and app ordering survive restarts and outages.
Also test weather failure independently of server failure, phone pairing,
container restarts and rollback. No performance or installation result is
claimed until those checks are run.

Before device installation, identify the TV on the network, verify its Android
version and debugging support, collect display/app preferences, and read back
the exact launcher/package changes and undo steps. The software and container
can be prepared before deploying them to either device.
