"""Integration check against the fictitious-TV local smoke container only."""
import json
import subprocess
import unittest


class ContainerIdentityTests(unittest.TestCase):
    container = "couch-tv-setup-check"

    def fingerprint(self):
        command = """import sys,hashlib,json;sys.path.insert(0,'/app/bridge');import tv;from pathlib import Path
assert all((t.get('host') or t.get('ip'))=='tv.example.org' for t in tv.config.TVS)
p=Path(tv.ensure_adb_key());print(json.dumps({'path':str(p),'sha':hashlib.sha256(p.read_bytes()).hexdigest()}))"""
        return json.loads(subprocess.check_output(["docker", "exec", self.container, "python", "-c", command]))

    def test_adb_identity_survives_container_restart(self):
        first = self.fingerprint()
        self.assertEqual(first["path"], "/data/adbkey")
        subprocess.run(["docker", "restart", self.container], check=True, capture_output=True)
        self.assertEqual(self.fingerprint(), first)


if __name__ == "__main__":
    unittest.main()
