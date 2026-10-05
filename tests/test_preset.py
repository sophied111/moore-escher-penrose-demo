import re
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parent.parent
_PRESET = _ROOT / "configs" / "flux_conformal.yaml"


def test_preset_ships_with_the_demo_and_is_valid():
    # escher's configs/ live at its repo root, outside the installed package, so
    # the pip wheel does NOT ship them — the demo must vendor the preset itself.
    assert _PRESET.is_file(), "configs/flux_conformal.yaml must ship in the demo repo"
    data = yaml.safe_load(_PRESET.read_text(encoding="utf-8"))
    assert data["backbone"] == "flux"
    assert data["upres"] == "sr"
    assert "num_steps" in data


def test_app_loads_preset_by_path_not_bare_name():
    src = (_ROOT / "app.py").read_text(encoding="utf-8")
    # Must resolve a real file path next to app.py, not the bare "flux_conformal"
    # (which escher would look for beside the installed package — absent there).
    assert "flux_conformal.yaml" in src
    assert re.search(r"load_preset\(\s*_PRESET_PATH", src)
