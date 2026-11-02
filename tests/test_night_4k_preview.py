"""Night-only visual experiment. Browser plugin not available; using Playwright.

Run: .venv/bin/python -m unittest discover -s tests -p test_night_4k_preview.py -v
"""
import importlib.util
from io import BytesIO
from functools import partial
from pathlib import Path
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("night_test", ROOT / "tv-home/tools/night-4k-test.py")
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)


class NightPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = preview.ThreadingHTTPServer(("127.0.0.1", 0),
            partial(preview.PreviewHandler, directory=str(ROOT)))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_layer_integrity(self):
        preview.check()

    def test_connected_home_keeps_native_continue_when_bridge_is_empty(self):
        self.check_connected_continue([], "TV sample episode")

    def test_connected_home_prefers_nonempty_bridge_continue(self):
        self.check_connected_continue([{"id": "bridge-1", "title": "Bridge sample episode"}],
                                      "Bridge sample episode")

    def check_connected_continue(self, bridge_items, expected):
        from test_web_home import NATIVE
        page = self.browser.new_page(viewport={"width": 1920, "height": 1080})
        self.addCleanup(page.close)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.add_init_script(NATIVE + "\nwindow.TVOS.watchNext = () => JSON.stringify(["
            "{id:'native-1',title:'TV sample episode',kind:'watchnext'}]);")
        import json
        page.route("**/config.js", lambda route: route.fulfill(content_type="text/javascript", body=
            'window.COUCH_CONFIG={people:[],home:{look:"night",scenes:["night"]}};'))
        def api(route):
            route.fulfill(content_type="application/json", body=json.dumps({"ok": True,
                "people": [], "items": bridge_items, "screens": [], "apps": []}))
        page.route("**/api/**", api)
        page.route("https://**/*", lambda route: route.abort())
        page.goto(self.url + "/tv-home/web/index.html")
        page.locator("#grid").get_by_text("Netflix", exact=True).wait_for(state="attached")
        page.wait_for_function("!document.getElementById('shelf-section').classList.contains('empty')", timeout=4000)
        self.assertIn(expected, page.locator("#shelf").inner_text())
        self.assertFalse(errors, errors)

    def test_icon_source_sizes_and_browser_comparison(self):
        from PIL import Image
        logo = "com.netflix.ninja.png"
        for variant, size in (("original", 128), ("candidate", 256)):
            data = urlopen(self.url + "/icon-test/" + variant + "/" + logo).read()
            with Image.open(BytesIO(data)) as image:
                self.assertEqual(image.size, (size, size))
        page = self.browser.new_page(viewport={"width": 1440, "height": 1100})
        self.addCleanup(page.close)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route("https://**/*", lambda route: route.abort())
        page.goto(self.url + "/docs/previews/icons-2x.html")
        self.assertEqual(page.title(), "Icon resolution comparison")
        for title, size in (("128px icon dashboard", 128), ("256px icon dashboard", 256)):
            scope = page.frame_locator('iframe[title="' + title + '"]')
            scope.locator("#grid img").first.wait_for(state="visible")
            self.assertEqual(scope.locator("#grid img").first.evaluate("el => el.naturalWidth"), size)
            self.assertNotIn("night-4k-test", scope.locator(".scene.on .sbg").get_attribute("src"))
        for frame in page.frames[1:]:
            frame.wait_for_function("document.querySelector('.scene.on .sbg').naturalWidth > 0 && document.fonts.status === 'loaded'")
            frame.add_style_tag(content="*, *::before, *::after { animation: none !important; transition: none !important; }")
        page.wait_for_function("[...document.querySelectorAll('.logos img')].every(i => i.complete && i.naturalWidth > 0)")
        output = ROOT / "build/night-4k"
        output.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(output / "icon-comparison.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        self.assertEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
        self.assertFalse(errors, errors)

    def test_server_excludes_private_files_and_original_js_is_unchanged(self):
        for path in ("/config.json", "/.env", "/build/setup-status.json",
                     "/candidate/config.json", "/tv-home/web/backgrounds/mine/",
                     "/candidate/tv-home/web/backgrounds/mine/"):
            with self.subTest(path=path), self.assertRaises(HTTPError) as caught:
                urlopen(self.url + path)
            self.assertEqual(caught.exception.code, 404)
        source = (ROOT / "tv-home/web/app.js").read_bytes()
        self.assertEqual(urlopen(self.url + "/tv-home/web/app.js").read(), source)
        candidate = urlopen(self.url + "/candidate/tv-home/web/app.js").read()
        self.assertEqual(candidate, source.replace(b'photo: "scene-night", fg: true, glass: true',
            b'photo: "night-4k-test/scene-night", fg: true, glass: true'))
        with self.assertRaises(HTTPError) as caught:
            urlopen(Request(self.url + "/config.json", method="HEAD"))
        self.assertEqual(caught.exception.code, 405)

    def test_comparison_and_clock_alignment_at_both_resolutions(self):
        context = self.browser.new_context(viewport={"width": 1440, "height": 1100},
                                           timezone_id="UTC", device_scale_factor=1)
        self.addCleanup(context.close)
        # Stable, matching time in both iframes; screenshots contain only mock data.
        context.add_init_script("""{
          const RealDate = Date;
          window.Date = class extends RealDate {
            constructor(...args) { super(...(args.length ? args : ['2026-11-01T12:34:00Z'])); }
          };
        }""")
        context.route("https://**/*", lambda route: route.abort())
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(self.url + "/docs/previews/night-4k.html")
        self.assertEqual(page.title(), "Night scene · 4K experiment")
        frames = [page.frame_locator('iframe[title="' + title + '"]') for title in
                  ("Original Night dashboard", "4K Night dashboard")]
        for frame in frames:
            frame.locator(".scene.on .sbg").wait_for(state="visible")
        for child in page.frames[1:]:
            child.locator("#grid img").first.wait_for(state="visible")
            child.wait_for_function("document.querySelector('.scene.on .sbg').complete && "
                "document.querySelector('.scene.on .fg').complete && document.fonts.status === 'loaded' && "
                "[...document.querySelectorAll('#grid img')].every(i => i.complete && i.naturalWidth > 0)")
            child.add_style_tag(content="*, *::before, *::after { animation: none !important; transition: none !important; }")
        original, candidate = page.frames[1:]
        self.assertEqual(original.evaluate("innerWidth"), 3840)
        self.assertEqual(candidate.evaluate("innerWidth"), 3840)
        for child, natural in ((original, 1920), (candidate, 3840)):
            self.assertEqual(child.locator(".scene.on .sbg").evaluate("el => el.naturalWidth"), natural)
            self.assertEqual(child.locator(".scene.on .fg").evaluate("el => el.naturalWidth"), natural)
        geometry = """() => ['.scene.on .sbg', '.scene.on .fg', '.scene.on .gclock',
          '.scene.on .gclock .fill'].map(s => {
            const el = document.querySelector(s), r = el.getBoundingClientRect(), c = getComputedStyle(el);
            return [r.x, r.y, r.width, r.height, c.backgroundSize, c.backgroundPosition, el.textContent];
          })"""
        self.assertEqual(original.evaluate(geometry), candidate.evaluate(geometry))
        self.assertIn("night-4k-test", candidate.locator(".scene.on .fill").evaluate("el => el.style.backgroundImage"))
        self.assertNotIn("night-4k-test", original.locator(".scene.on .fill").evaluate("el => el.style.backgroundImage"))
        output = ROOT / "build/night-4k"
        output.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(output / "comparison.png"), full_page=True)
        page.get_by_role("button", name="4K test only", exact=True).click()
        self.assertTrue(page.locator('figure[data-version="original"]').is_hidden())
        self.assertEqual(page.get_by_role("button", name="4K test only", exact=True).get_attribute("aria-pressed"), "true")
        page.get_by_role("button", name="Side by side", exact=True).click()
        self.assertTrue(page.locator('figure[data-version="original"]').is_visible())
        # Mobile-sized comparison layout, then native-resolution dashboard captures.
        page.set_viewport_size({"width": 390, "height": 844})
        self.assertEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
        page.screenshot(path=str(output / "comparison-mobile.png"), full_page=True)
        for variant, path in (("original", "/tv-home/web"), ("candidate", "/candidate/tv-home/web")):
            standalone = context.new_page()
            standalone.set_viewport_size({"width": 3840, "height": 2160})
            standalone.goto(self.url + path + "/index.html?mock=1&reset=1&scenes=night&clock=24h&people=0")
            standalone.locator(".scene.on .sbg").wait_for(state="visible")
            standalone.locator("#grid img").first.wait_for(state="visible")
            standalone.wait_for_function("[...document.querySelectorAll('#grid img, .scene.on img')].every(i => i.complete && i.naturalWidth > 0) && document.fonts.status === 'loaded'")
            standalone.add_style_tag(content="*, *::before, *::after { animation: none !important; transition: none !important; }")
            standalone.screenshot(path=str(output / (variant + "-4k.png")))
            standalone.set_viewport_size({"width": 1920, "height": 1080})
            standalone.reload()
            standalone.locator(".scene.on .fg").wait_for(state="visible")
            self.assertEqual(standalone.locator(".scene.on .sbg").bounding_box()["width"], 1920)
            self.assertEqual(standalone.locator(".scene.on .fg").bounding_box()["width"], 1920)
            standalone.close()
        self.assertFalse(errors, errors)
