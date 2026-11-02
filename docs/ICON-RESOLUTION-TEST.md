# Icon rendering experiment

For the TCL 85QM850G (85 inches), the launcher has an opt-in build flag:
`-PiconRenderScale=2`. The default is `1` and retains existing dimensions.
No TV installation is part of this experiment.

| Asset | Normal build | Opt-in test build |
| --- | --- | --- |
| Square app icons | 128 × 128 | 256 × 256 |
| TV app banners | 640 × 360 | 1280 × 720 |
| Fallback icon-tile working image | 432 × 432 | 864 × 864 |

The test renders the app's own Android drawables at twice the raster resolution,
including both layers of adaptive icons. Canvas scaling retains the original
logical tile coordinates and logo proportions. Logo bounds are still sampled in
the same logical coordinates. The fallback tile uses its higher-resolution
working image for the final draw. No branding is generated or replaced.

The test uses separate banner disk-cache keys and versioned icon/banner URLs,
so old browser/disk caches do not conceal the candidate and normal builds can
continue using the original cache. Keep the old APK for any later device trial;
installing a test build requires separate approval. The app's own launcher icon
and UI symbols are already vectors and need no bitmap upscaling. This flag
applies to the Home launcher (options A/B), not the separate option-C app.

Run `night-4k-test.py --serve` as described in `NIGHT-4K-TEST.md`, then open
<http://127.0.0.1:8765/docs/previews/icons-2x.html>. The browser preview uses the
repository's sample PNG logos at 128px versus 256px; originals on disk remain
unchanged. Both dashboard previews use the original Night background to isolate
the icon difference. It is an illustration, not native Android raster evidence.

An experimental Android build can be compiled with the existing local toolchain:

```sh
cd tv-home/android
../../build/gradle-8.11.1/bin/gradle :app:testDebugUnitTest :app:assembleDebug -PiconRenderScale=2 -PconfigJson=../../../config.example.json
```

Use the repository's local JDK/SDK environment first. Omit `iconRenderScale` to
return to normal rendering in a later build. Neither command installs anything.
Each decoded raster contains four times as many pixels at 2x. Native cache memory,
TV performance and actual app artwork quality must be checked before deployment.

## Local verification (2026-11-01)

- Opt-in debug build compiled with generated `ICON_RENDER_SCALE = 2`.
- All eight existing Android unit tests passed in the opt-in build.
- A normal debug build also compiled, with generated `ICON_RENDER_SCALE = 1`.
- All four browser/asset tests passed, including the icon endpoint dimensions,
  both sample dashboard variants, mobile layout, and the earlier Night checks.
- Screenshot: ignored `build/night-4k/icon-comparison.png`.

These are compilation and desktop-browser checks. The actual Android drawable
raster output has not been captured on an emulator or physical TV.
