# Synology bridge

This fork uses a locally installed Android home app and a Python bridge in
Synology Container Manager. The bridge serves the phone remote and the server
copy of Home. The TV carries its own assets for server outages. This guide is
for Linux-based Synology NAS devices with Container Manager, such as DS923+.

## Prepare

Build an image for the NAS CPU architecture, then import it in Container Manager:

```sh
docker build --platform linux/amd64 -t couch-tv-bridge:local .
docker save -o couch-tv-bridge-amd64.tar couch-tv-bridge:local
```

Create a new project folder under the existing Docker share. Put `compose.yaml`
there (Container Manager accepts the filename `docker-compose.yml`), remove
`build: .` if importing a prebuilt image, and create `config/config.json` from
`config.example.json`. Enter the actual TV address, weather city and preferences.
Start with `paired: false`, `wake_on_lan: false`, `ask.enabled: false` and no
smart-home configuration. An unpaired Android TV entry is not connected by the
bridge. This fork also blocks ADB discovery, port checks, reconnection and wake
packets until remote pairing is complete, so opening the phone page cannot
trigger an ADB prompt on an unpaired TV. A reserved `setup-pending.invalid`
hostname can be used as an additional precaution during staging.

Create a private `.env` beside the Compose file containing
`COUCH_BIND_ADDRESS=<NAS LAN address>` and optionally `TZ=<time zone>`.
The default is loopback, so the bridge is not exposed to the LAN until an address
is explicitly configured. Keep the existing NAS firewall restricting access to
trusted LAN/VPN clients. Do not forward its port through the router. The upstream
phone remote has no application password: clients allowed to reach it can control
paired TVs. A guest network should not have access.

## Storage and startup

Create the Container Manager project from the Compose file. The image runs as
UID/GID 10001 with a read-only application filesystem and no extra capabilities.
The project creates two Docker-managed volumes with the correct ownership:

- `config` contains the writable runtime configuration. On the first run only,
  `/seed/config.json` is copied from the read-only `./config` folder.
- `data` contains pairing certificates, the persistent ADB key, app order,
  settings and viewing history. Restarting does not create a new ADB identity.

Restarting the bridge does not overwrite pairing changes with the initial seed.
After initialization, edit `/config/config.json` inside the container to change
runtime configuration; updating the seed alone intentionally does not replace
it. Restart after changes. Preserve these volumes when recreating the container;
deleting project volumes discards pairing and saved settings. Back up both
volumes using your existing container backup process. The seed is not a backup
of the current runtime configuration.

The phone page is `http://<NAS LAN address>:5400/`. Container Manager should report
the container healthy; `/api/health`, `/tv/` and `/tv/manifest.json` should answer.
An unpaired TV appearing unavailable is expected. Check the log for
`not paired yet, not connecting` before proceeding with TV installation.

## Pair later, when the TV is available

Do not start pairing or run the install script while someone is using the TV.
If staged with `setup-pending.invalid`, replace it with the verified TV address
in `/config/config.json` and restart the bridge only when the TV is available.
In Container Manager's terminal for the bridge, start:

```sh
python bridge/pair_tv.py <tv-id>
```

Read the fresh code on the TV and submit it in a second terminal:

```sh
python bridge/pair_tv.py <tv-id> --code <fresh-code>
```

Pairing updates the runtime configuration and stores certificates in the data
volume. Restart the bridge after pairing. Before enabling ADB, review the exact
launcher changes and [undo steps](UNINSTALL.md) with the user. Allow both the
installation computer and the bridge before disabling the stock launcher.

Build the customized TV APK with a persistent private signing key. Install that
build rather than an upstream release APK, which lacks these changes and is
signed differently. Keep the signing key outside Git. Updates target this fork;
upstream releases must be integrated, tested and rebuilt deliberately.

## Checks and rollback

First verify the TV's Home button and two app shortcuts, then stop only the new
bridge project to check local fallback. Also test an unreachable server, a slow
response, a TV restart without the server, and server recovery while navigating
and while playing video. The one-second fallback is a load budget, not a promise
that a cold WebView and all local assets render within one second.

To roll back the server, stop the couch-tv project and recreate it from the
previous image while retaining its volumes. Leave other projects alone. To
restore the original TV home, stop the bridge first, then follow
[UNINSTALL.md](UNINSTALL.md) and the saved per-TV undo record. Do not delete the
project's volumes until their settings and pairing data are no longer needed.
