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
    # The VCS pin's distribution name must be the package's real name ('escher',
    # from its pyproject), not the GitHub repo name — pip rejects a name @ url
    # whose declared name disagrees with the built metadata.
    assert "escher" in names, "pin the dist name 'escher', not the repo name"
    for banned in ("gradio", "spaces", "huggingface_hub", "huggingface-hub"):
        assert banned not in names, f"do not list {banned} (ZeroGPU platform-managed)"


def test_model_deps_pinned_to_flux_lock():
    # Track the paper's flux lock for the deps that drive the math, so the Space
    # output stays as close to the clean-code reference as ZeroGPU allows. torch
    # is intentionally NOT pinned (ZeroGPU supplies it); hub is platform-managed.
    reqs = Path("requirements.txt").read_text(encoding="utf-8")
    for pin in ("diffusers==0.37.1", "transformers==5.6.2", "accelerate==1.14.0",
                "tokenizers==0.22.2", "safetensors==0.7.0"):
        assert pin in reqs, f"pin {pin} to the flux lock"
