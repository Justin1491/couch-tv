import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("container_start", Path(__file__).parents[1] / "bridge/container_start.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ContainerStartTests(unittest.TestCase):
    def test_seed_initializes_config_but_restart_keeps_pairing_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seed, target = root / "seed.json", root / "config.json"
            seed.write_text('{"tvs": [{"id":"test","host":"tv.example.org","paired":false}]}')
            module.seed_config(target, seed)
            self.assertEqual(target.read_text(), seed.read_text())
            target.write_text('{"paired":true}')
            module.seed_config(target, seed)
            self.assertEqual(target.read_text(), '{"paired":true}')

    def test_missing_configuration_fails_instead_of_using_upstream_example(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(SystemExit, "config.json"):
                module.check_config(Path(d) / "config.json")

    def test_example_placeholder_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.json"
            path.write_text('{"tvs":[{"id":"test","ip":"SET_YOUR_TV_IP"}]}')
            with self.assertRaisesRegex(SystemExit, "address"):
                module.check_config(path)

    def test_real_configuration_is_accepted_without_modification(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.json"
            value = '{"tvs":[{"id":"test","host":"tv.example.org","paired":false}]}'
            path.write_text(value)
            module.check_config(path)
            self.assertEqual(path.read_text(), value)


if __name__ == "__main__":
    unittest.main()
