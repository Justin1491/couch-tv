# Night scene 4K experiment

Target display, as supplied by the owner: **TCL 85QM850G, 85 inches**.
The panel model does not establish the launcher's actual WebView render resolution;
that remains to be measured on the device in a separately approved test.

This branch tests only Night. All original backgrounds, optical glass fills,
foreground cutouts, icons, clock geometry, and production application code stay
unchanged. Nothing is installed on or sent to the TV or NAS.

## Method

The first candidate uses local Pillow Lanczos interpolation, uniformly 2× in both
dimensions, from 1920 × 1080 to 3840 × 2160. This is a conservative resizing
baseline, **not AI super-resolution or a true 4K original**. Expect modest changes
at most. JPEG outputs use quality 95 and no chroma subsampling; the foreground
is a lossless WebP with its resized alpha mask retained. The existing glass fill
is enlarged with the same mapping so its visual blur and color treatment remain
consistent with the original. Nothing is cropped, reimagined, or sharpened.

The candidates live in `tv-home/web/backgrounds/night-4k-test/`. Its manifest
records source/output checksums, sizes and the Pillow version. Existing scene
definitions and default asset paths are untouched. Only the loopback preview
server substitutes Night's asset path in the candidate response for `app.js`;
the source file on disk remains unchanged. A changed scene definition causes
the preview to fail visibly rather than silently compare the wrong images.

## Run and compare

With Python 3.11+ and Pillow installed in the project's Python environment
(`tv-home/tools/night-4k-requirements.txt` pins the version used here):

```sh
.venv/bin/python tv-home/tools/night-4k-test.py --check
.venv/bin/python tv-home/tools/night-4k-test.py --serve
```

Open <http://127.0.0.1:8765/docs/previews/night-4k.html>. Use Side by side or
switch between Original only and 4K test only. Inspect the clock's intersection
with the mountain and the matching detail crops. Full images are linked too.
Both dashboard frames have a 3840 × 2160 viewport, scaled down to fit the page.
Sample shows/apps are synthetic, and the preview uses no personal config.
The server exposes only the public web assets, logos and preview directory,
binds only to loopback, and never connects to the TV or bridge.

To reproduce the candidates from the untouched sources, omit the flag:

```sh
.venv/bin/python tv-home/tools/night-4k-test.py
```

Browser validation uses Playwright because the Browser plugin/skill is not
available. See `tests/test_night_4k_preview.py` for the repeatable checks.

Validation on 2026-11-01: all three tests passed. Checks cover layer hashes,
4K dimensions and alpha, matching clock/foreground geometry at 4K, both variants
at 1080p, original-only and side-by-side controls, a 390-pixel comparison layout,
no JavaScript page errors in the comparison, and exclusion of private files.
Generated screenshots stay ignored under `build/night-4k/`: `comparison.png`,
`comparison-mobile.png`, `original-4k.png`, and `candidate-4k.png`.
Visual review found the expected subtle change in mountain-edge interpolation;
this resize does not restore missing source texture or establish a TV benefit.

## Decision and undo

Review visual quality first. Before adopting any 4K assets, separately measure
the TV's effective render resolution, loading, transitions and memory use.
Doubling width and height uses four times the decoded pixels: one RGBA layer
is about 31.6 MiB at 4K versus 7.9 MiB at 1080p, before other rendering overhead.
Browser timing is not a substitute for physical-TV testing.

Icons are deliberately outside this Night-only experiment. A later test can
render installed apps' original drawables at greater resolution without
redrawing their branding. AI super-resolution would also be a separately
labeled candidate, with new glass generation and skyline-edge checks.

Stop the preview with Ctrl-C and switch back to `main` to leave the experiment.
There is no device rollback step because no device is changed. Keep the PR
unmerged until the comparison is accepted; merging does not authorize deployment.
