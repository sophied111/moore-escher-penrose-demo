import re
from pathlib import Path


def _dist_name(requirement_line: str) -> str:
    """Distribution name from a requirement line (before any version/extra/url spec)."""
    return re.split(r"[\s=<>!~\[@]", requirement_line, maxsplit=1)[0].strip().lower()


def test_dist_name_parses_versioned_and_url_requirements():
    assert _dist_name("gradio==6.29.1") == "gradio"
    assert _dist_name("spaces>=0.30") == "spaces"
    assert _dist_name("moore-escher-penrose[flux] @ git+https://x@sha") == "moore-escher-penrose"


def _frontmatter():
    text = Path("README.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "README.md must start with a YAML frontmatter block"
    import yaml
    return yaml.safe_load(m.group(1))


def test_required_frontmatter_keys():
    fm = _frontmatter()
    assert fm["sdk"] == "gradio"
    assert fm["app_file"] == "app.py"
    assert str(fm["python_version"]) == "3.12"
    assert len(fm["short_description"]) <= 60


def test_requirements_pin_is_frozen():
    reqs = Path("requirements.txt").read_text(encoding="utf-8")
    pkg_lines = [
        ln.strip() for ln in reqs.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert any("moore-escher-penrose" in ln for ln in pkg_lines)
    for ln in pkg_lines:
        assert "@main" not in ln, "pin an immutable SHA/tag, never @main"
    names = [_dist_name(ln) for ln in pkg_lines]
    for banned in ("gradio", "spaces", "huggingface_hub"):
        assert banned not in names, f"do not list {banned}"
