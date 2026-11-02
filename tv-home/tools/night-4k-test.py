#!/usr/bin/env python3
"""Build/check a non-destructive Night resize experiment, or serve its local preview.

Requires Pillow. Does not connect to a TV or use personal configuration.
"""
import argparse
import hashlib
import json
from io import BytesIO
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[2]
BACKGROUNDS = ROOT / "tv-home/web/backgrounds"
DEST = BACKGROUNDS / "night-4k-test"
FILES = ("scene-night.jpg", "scene-night-glass.jpg", "scene-night-fg.webp")
SIZE = (3840, 2160)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    from PIL import Image, __version__
    DEST.mkdir(exist_ok=True)
    records = []
    for name in FILES:
        source, target = BACKGROUNDS / name, DEST / name
        with Image.open(source) as image:
            if image.size != (1920, 1080):
                raise ValueError(f"Unexpected source size for {name}: {image.size}")
            mode = "RGBA" if name.endswith(".webp") else "RGB"
            # The same mapping for photo, optical fill, and alpha mask; no recrop,
            # sharpening, color adjustment, or generative changes to move edges.
            enlarged = image.convert(mode).resize(SIZE, Image.Resampling.LANCZOS)
            if mode == "RGBA":
                enlarged.save(target, lossless=True, exact=True, method=6)
            else:
                enlarged.save(target, quality=95, subsampling=0, optimize=True)
        records.append({"file": name, "source_sha256": digest(source),
                        "output_sha256": digest(target), "output_bytes": target.stat().st_size})
    manifest = {"method": "Pillow Lanczos 2x; no AI enhancement", "pillow": __version__,
                "source_size": [1920, 1080], "output_size": list(SIZE), "assets": records}
    (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    check()


def check():
    from PIL import Image
    manifest = json.loads((DEST / "manifest.json").read_text())
    if [r["file"] for r in manifest["assets"]] != list(FILES):
        raise ValueError("Incomplete asset manifest")
    for record in manifest["assets"]:
        source, target = BACKGROUNDS / record["file"], DEST / record["file"]
        if digest(source) != record["source_sha256"] or digest(target) != record["output_sha256"]:
            raise ValueError(f"Asset changed: {record['file']}")
        with Image.open(target) as image:
            image.load()
            if image.size != SIZE:
                raise ValueError(f"Not 4K: {target.name}")
            if target.suffix == ".webp":
                alpha = image.getchannel("A")
                if alpha.getextrema() != (0, 255):
                    raise ValueError("Foreground lost its transparent sky or opaque scenery")
    print("PASS: all three 4K layers decode, alpha retained, original and candidate hashes match")


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self.send_error(405, "This preview serves GET requests only")

    def translate_path(self, path):
        # Use the already decoded, checked path; avoid a second URL decode in
        # SimpleHTTPRequestHandler that could turn literal % sequences into ../.
        return str(self.public_path)

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        icon_variant = None
        for variant in ("original", "candidate"):
            prefix = "/icons-" + variant + "/"
            if path.startswith(prefix):
                icon_variant = variant
                path = path[len(prefix) - 1:]
                break
        candidate = path.startswith("/candidate/")
        if candidate:
            path = path[len("/candidate"):]
        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/docs/previews/night-4k.html")
            self.end_headers()
            return
        if path.startswith("/icon-test/"):
            # Preview the old 128px raster limit versus the bundled 256px PNGs.
            # These sample logos are not actual installed-TV drawable captures.
            from PIL import Image
            parts = path.split("/")
            if (len(parts) != 4 or parts[2] not in ("original", "candidate")
                    or not parts[3].endswith(".png")):
                self.send_error(404)
                return
            source = ROOT / "remote/src/app-logos" / parts[3]
            if not source.is_file():
                self.send_error(404)
                return
            with Image.open(source) as logo:
                size = 128 if parts[2] == "original" else 256
                output = BytesIO()
                logo.resize((size, size), Image.Resampling.LANCZOS).save(output, format="PNG")
                self.send_body(output.getvalue(), "image/png")
                return
        # Only public artwork and the mock page are served, never config.json,
        # .env, pairing data, or the bridge. Bind to loopback only below.
        resolved = (ROOT / path.lstrip("/")).resolve()
        allowed = (ROOT / "tv-home/web", ROOT / "remote/src/app-logos", ROOT / "docs/previews")
        private_photos = ROOT / "tv-home/web/backgrounds/mine"
        if (not any(resolved.is_relative_to(folder) for folder in allowed)
                or resolved.is_relative_to(private_photos)):
            self.send_error(404)
            return
        if path == "/tv-home/web/config.js":
            body = b"window.COUCH_CONFIG = {};"
            content_type = "text/javascript"
        elif icon_variant and path == "/tv-home/web/mock.js":
            script = resolved.read_text()
            original = '"../../remote/src/app-logos/"'
            if script.count(original) != 1:
                self.send_error(500, "Mock icon path changed; preview needs review")
                return
            body = script.replace(original, '"/icon-test/' + icon_variant + '/"').encode()
            content_type = "text/javascript"
        elif candidate and path == "/tv-home/web/app.js":
            original = 'photo: "scene-night", fg: true, glass: true'
            script = resolved.read_text()
            if script.count(original) != 1:
                self.send_error(500, "Night scene definition changed; preview needs review")
                return
            body = script.replace(original, 'photo: "night-4k-test/scene-night", fg: true, glass: true').encode()
            content_type = "text/javascript"
        else:
            self.public_path = resolved
            self.path = path
            return super().do_GET()
        self.send_body(body, content_type)

    def send_body(self, body, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true")
    action.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.serve:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(PreviewHandler, directory=str(ROOT)))
        print(f"Preview: http://127.0.0.1:{server.server_port}/docs/previews/night-4k.html", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    elif args.check:
        check()
    else:
        build()


if __name__ == "__main__":
    main()
