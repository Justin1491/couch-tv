# Upstream main deployment verification

The owner authorized deploying the integration at `e57dd7d` to the existing Synology bridge and TCL TV, retaining their settings and pairing, and verifying the cinematic mobile icon. The owner also authorized replacing the old bridge container and using a disabled, manually run DSM root task when Container Manager's controls failed.

## Synology

- Deployed `couch-tv-bridge:main-e57dd7d` for Linux/amd64. The imported image configuration digest is `4542032f22225fd4194440761b5a20e5b227726441673481b9223687a20d1df5`, verified against the archive's configuration bytes before replacement. Docker Desktop reports the manifest digest instead; these identifiers must not be compared as if they were the same kind of digest.
- Docker located exactly one running container using the `com.docker.compose.project=couch-tv` and `com.docker.compose.service=bridge` labels. The old image was verified before stopping and removing that container. Its named configuration and data volumes were preserved.
- Compared the deployed Compose file with its previous contents: only the image tag changed. Host networking, bind settings, volume layout, read-only filesystem and other existing options were retained.
- DSM reported the manual task completed with `Normal (0)`. The task remains disabled and has no automatic execution enabled. Other projects were outside the deployment.
- Health, TV pairing, remote connection and ADB checks succeeded after replacement. Existing people IDs were retained. The phone remote's normal HTTP Home command succeeded.
- The live `app.js`, `weather-cache.js` and home HTML matched the integrated source, accounting for the bridge's HTML metadata insertion.

## Mobile icon

All four `test_mobile_site.py` checks passed against the live NAS. They verified the favicon and Apple Home Screen links, cinematic onboarding artwork in the served bundle, every manifest icon's exact PNG bytes, legacy icon URLs, revalidation headers, the bridge helper, and the newly packaged platform assets.

Existing Home Screen bookmarks may retain their operating system's cached icon. The server serves cinematic artwork at both the current and legacy URLs; removing and adding an old bookmark again can refresh its stored image.

## TV

- Backed up the installed 0.6/code 8 APK before updating. Built the integration using the existing private signing key and the NAS's current public display settings. The signing certificate matched the installed app before installation.
- Installed Home 0.12/code 14 from integrated main. The installed APK's SHA-256 matched the signed deployment build; the package remains `app.couchtv.launcher`.
- Verified couch-tv remained the default Home. Netflix and Disney+ opened without starting playback, and Home returned to couch-tv after each. Basic directional navigation worked. After the full TV reboot, both apps were checked again and the live phone-remote Home command returned to couch-tv after each.
- Inspected the settled home: backgrounds, clock, weather, artwork, app tiles and Continue Watching rendered. Reloaded Home after replacing the bridge and verified it was foreground and still the default launcher.
- After the bridge replacement and a Home-page reload, the TV showed a blank native background. Restarting the app did not restore it. The owner suggested restarting the TV; one full reboot restored the visible home. A changed boot ID and completed Android boot were verified, couch-tv remained foreground/default, and pairing, remote connection and ADB reconnected. The cause of the transient blank screen remains unconfirmed. No fatal crash appeared in the earlier process-log sample; a later log read timed out, and the focused pre-reboot log had no useful error entries. This is not a long-duration reliability test.

## Rollback and private evidence

The previous NAS image, `couch-tv-bridge:upstream-118d8cc`, is retained. The existing project folder contains `rollback-e57dd7d/` with the previous Compose file, container metadata, and nonempty configuration/data archives. Restore the previous image tag and recreate only the couch-tv service while retaining its volumes. The archives are available if data restoration is required; do not delete volumes as part of an image rollback.

The previous TV APK and signed deployment APK are retained in the ignored local `build/main-deployment-e57dd7d/` folder alongside hashes, logs, configuration comparisons and screenshots. These private deployment artifacts are not committed. Restoring the earlier APK can require an Android version downgrade; preserve app data and use the existing signing identity rather than uninstalling blindly. To remove couch-tv entirely, follow [UNINSTALL.md](../../UNINSTALL.md), stopping the bridge first.

DSM's displayed container name was stale, and its project controls opened an empty terminal instead of applying changes. Early guarded task attempts exited before stopping anything. The completed deployment used the verified Docker labels and archive configuration digest through the owner's approved fixed-path manual task.
