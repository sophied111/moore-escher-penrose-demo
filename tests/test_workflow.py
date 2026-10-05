from pathlib import Path

import yaml


def test_workflow_parses_and_targets_the_space():
    wf = yaml.safe_load(Path(".github/workflows/deploy.yml").read_text(encoding="utf-8"))
    # PyYAML parses the bare `on:` key as the boolean True — assert on that.
    assert True in wf or "on" in wf
    body = Path(".github/workflows/deploy.yml").read_text(encoding="utf-8")
    assert "SophieD/moore-escher-penrose-demo" in body  # HF Space id (HF user, not GitHub)
    assert "--repo-type space" in body
    assert "HF_TOKEN" in body
