"""Integration checks against the synthetic, loopback-only bridge used by test_web_home.

Run after building the remote and local container, with COUCH_TEST_URL set to its base URL.
"""
import hashlib
import json
import os
from pathlib import Path
import unittest
from urllib.request import urlopen

ROOT = Path(__file__).parents[1]
URL = os.environ.get("COUCH_TEST_URL", "http://127.0.0.1:15400/tv/").split("/tv/")[0].rstrip("/")


class MobileSiteTests(unittest.TestCase):
    def get(self, path, revalidate=True):
        with urlopen(URL + path, timeout=5) as response:
            self.assertEqual(response.status, 200)
            if revalidate:
                self.assertIn("no-cache", response.headers.get("Cache-Control", ""))
            return response.read(), response.headers.get_content_type()

    def test_mobile_page_and_onboarding_use_cinematic_art(self):
        html = self.get("/")[0].decode()
        self.assertIn('rel="icon" href="/icons/cinematic-192.png"', html)
        self.assertIn('rel="apple-touch-icon" href="/icons/cinematic-apple.png"', html)
        self.assertIn('src="/bridge/shim.js"', html)
        import re
        scripts = re.findall(r'<script[^>]*src="([^"]+)"', html)
        bundles = [self.get(path)[0] for path in scripts if path.startswith("/assets/")]
        self.assertTrue(bundles)
        self.assertTrue(any(b"/icons/cinematic-192.png" in content for content in bundles))
        self.assertIn(b"couch", self.get("/bridge/shim.js")[0].lower())

    def test_bridge_serves_phone_settings_and_its_scripts(self):
        html = self.get("/setup")[0].decode()
        for name in ("shim.js", "connect-check.js"):
            with self.subTest(name=name):
                path = "/ontv/" + name
                self.assertIn('src="' + path + '"', html)
                self.assertEqual(self.get(path)[0], (ROOT / "on-tv/web" / name).read_bytes())

    def test_manifest_icons_serve_the_expected_image_bytes(self):
        body, content_type = self.get("/manifest.webmanifest")
        self.assertEqual(content_type, "application/manifest+json")
        icons = json.loads(body)["icons"]
        self.assertEqual({icon["src"] for icon in icons}, {
            "/icons/cinematic-192.png", "/icons/cinematic-512.png",
            "/icons/cinematic-maskable-512.png", "/icons/cinematic-apple.png"})
        for icon in icons:
            with self.subTest(icon=icon["src"]):
                data, content_type = self.get(icon["src"])
                self.assertEqual(content_type, "image/png")
                expected = (ROOT / "remote/public" / icon["src"].lstrip("/")).read_bytes()
                self.assertEqual(hashlib.sha256(data).digest(), hashlib.sha256(expected).digest())

    def test_legacy_icon_urls_also_serve_cinematic_art(self):
        for legacy, current in (("icon-192.png", "cinematic-192.png"),
                                ("icon-512.png", "cinematic-512.png"),
                                ("apple-touch-icon.png", "cinematic-apple.png")):
            with self.subTest(icon=legacy):
                data, content_type = self.get("/icons/" + legacy)
                self.assertEqual(content_type, "image/png")
                self.assertEqual(data, (ROOT / "remote/public/icons" / current).read_bytes())

    def test_new_bridge_platform_assets_are_packaged(self):
        body, content_type = self.get("/titan/")
        self.assertEqual(content_type, "text/html")
        self.assertNotIn(b"Not built yet", body)
        self.assertIn(b"<script", body)
        data, content_type = self.get("/vidaa/icon.png", revalidate=False)
        self.assertEqual(content_type, "image/png")
        self.assertEqual(data, (ROOT / "lg/app/largeIcon.png").read_bytes())
