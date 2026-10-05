import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def test_preset_is_not_vendored():
    # escher >= v0.1.1 ships its presets as package data (resolved via
    # importlib.resources), so the demo must NOT carry its own copy.
    assert not (_ROOT / "configs").exists(), "drop vendored configs/; escher ships presets"


def test_app_loads_preset_by_bare_name():
    src = (_ROOT / "app.py").read_text(encoding="utf-8")
    assert re.search(r'load_preset\(\s*["\']flux_conformal["\']\s*\)', src), \
        "load the bundled preset by bare name now that escher ships it"
