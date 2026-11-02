"""Container entry point: require private configuration instead of silently using the example."""
import json
import os
from pathlib import Path
import sys


def seed_config(target, seed):
    if not target.exists() and seed.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation keeps an existing paired configuration authoritative.
        with target.open("x") as output:
            output.write(seed.read_text())
        target.chmod(0o600)


def check_config(path):
    try:
        settings = json.loads(path.read_text())
        tvs = settings.get("tvs")
        if not isinstance(tvs, list) or not tvs:
            raise ValueError("missing TVs")
        for tv in tvs:
            address = tv.get("host") or tv.get("ip")
            if not tv.get("id") or not isinstance(address, str) or not address.strip() or "SET_YOUR" in address:
                raise ValueError("set each TV address")
    except (OSError, ValueError, TypeError, AttributeError) as error:
        raise SystemExit("Provide a valid writable /config/config.json with each TV address before starting the bridge.") from error


if __name__ == "__main__":
    target = Path(os.environ.get("COUCH_CONFIG", "/config/config.json"))
    seed_config(target, Path(os.environ.get("COUCH_SEED_CONFIG", "/seed/config.json")))
    check_config(target)
    os.execv(sys.executable, [sys.executable, str(Path(__file__).with_name("server.py"))])
