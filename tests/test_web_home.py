"""Rendered home checks against a local bridge with a fictitious, unpaired TV.

Browser plugin not available; Playwright is used for repeatable app tests.
Run with COUCH_TEST_URL pointing at the local test container's /tv/ endpoint.
"""
import json
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

URL = os.environ.get("COUCH_TEST_URL", "http://127.0.0.1:15400/tv/")
ROOT = Path(__file__).parents[1]
NATIVE = """
window.launched = [];
window.TVOS = {
  apps: () => JSON.stringify([{package:'test.netflix',label:'Netflix'}, {package:'test.plex',label:'Plex'}]),
  kept: key => localStorage.getItem('native:' + key),
  keep: (key, value) => localStorage.setItem('native:' + key, value),
  launch: pkg => { window.launched.push(pkg); return true; },
  iconUrl: () => 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"/>',
  bannerUrl: () => 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"/>',
  version: () => 'test', watchNext: () => '[]', canOpenInputs: () => false
};
"""


class WebHomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1920, "height": 1080})
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.add_init_script(NATIVE)
        self.page.route("**/api.open-meteo.com/**", lambda route: route.fulfill(
            content_type="application/json", body=json.dumps({"current": {
                "temperature_2m": 24, "weather_code": 0, "is_day": 1}})))

    def tearDown(self):
        self.page.close()

    def test_offline_home_is_quiet_and_launches_apps_directly(self):
        self.page.goto(URL + "?offline=1")
        self.page.locator("#grid").get_by_text("Netflix", exact=True).wait_for(state="attached")
        self.assertEqual(self.page.locator("#status").inner_text(), "")
        self.assertTrue(self.page.locator("#time").inner_text())
        self.page.keyboard.press("Enter")
        self.page.wait_for_function("window.launched.length > 0")
        self.assertEqual(self.page.evaluate("window.launched[0]"), "test.netflix")
        self.assertFalse(self.errors, self.errors)
        (ROOT / "build").mkdir(exist_ok=True)
        self.page.screenshot(path=str(ROOT / "build/home-offline.png"))

    def test_weather_survives_failed_refresh_then_expires(self):
        self.page.goto(URL + "?offline=1")
        self.page.locator(".wx").wait_for()
        self.page.route("**/api.open-meteo.com/**", lambda route: route.abort())
        self.page.reload()
        self.page.locator(".wx").wait_for()
        self.assertIn("Updated", self.page.locator(".wx").get_attribute("title"))
        self.page.evaluate("""() => {
          var key='native:tvhome.weather', record=JSON.parse(localStorage.getItem(key));
          record.accepted=Date.now()-2*60*60*1000; localStorage.setItem(key,JSON.stringify(record));
        }""")
        self.page.reload()
        self.page.locator("#grid").wait_for()
        self.assertEqual(self.page.locator(".wx").count(), 0)
        self.assertEqual(self.page.locator("#status").inner_text(), "")
        self.assertFalse(self.errors, self.errors)

    def test_unreachable_bridge_keeps_live_page_quiet(self):
        self.page.route("**/api/**", lambda route: route.abort())
        self.page.goto(URL)
        self.page.locator("#grid").get_by_text("Netflix", exact=True).wait_for(state="attached")
        self.page.wait_for_timeout(100)
        self.assertEqual(self.page.locator("#status").inner_text(), "")
        self.assertFalse(self.errors, self.errors)


if __name__ == "__main__":
    unittest.main()
