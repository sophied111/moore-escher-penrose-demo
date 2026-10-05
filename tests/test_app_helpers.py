import os

os.environ["ESCHER_DEMO_SKIP_BACKBONE"] = "1"

import gradio as gr
import pytest

import app


def test_coerce_seed_accepts_int_and_str():
    assert app._coerce_seed(7) == 7
    assert app._coerce_seed("1234") == 1234


def test_coerce_seed_wraps_into_valid_range():
    # Negative / huge values are wrapped into [0, 2**32), never crash.
    s = app._coerce_seed(-1)
    assert 0 <= s < 2**32
    big = app._coerce_seed(10**30)
    assert 0 <= big < 2**32


def test_coerce_seed_rejects_garbage():
    with pytest.raises(gr.Error):
        app._coerce_seed("not-a-number")


def test_friendly_zerogpu_error_maps_quota():
    err = app._friendly_zerogpu_error(RuntimeError("ZeroGPU quota exceeded: 60s requested vs. 30s left"))
    assert isinstance(err, gr.Error)
    assert "quota" in str(err).lower()


def test_friendly_zerogpu_error_maps_illegal_duration():
    err = app._friendly_zerogpu_error(RuntimeError("ZeroGPU illegal duration"))
    assert isinstance(err, gr.Error)
    assert "limit" in str(err).lower()


def test_friendly_zerogpu_error_generic_for_unknown():
    err = app._friendly_zerogpu_error(RuntimeError("CUDA out of memory"))
    assert isinstance(err, gr.Error)
    assert "quota" not in str(err).lower() and "limit" not in str(err).lower()


def test_estimate_duration_within_free_tier_cap():
    # The duration callable is invoked by @spaces.GPU with _run's exact args:
    # (prompt, seed, family, progress). It must declare <= the free-tier 120s
    # per-call cap, or ZeroGPU rejects the call with "illegal duration".
    d = app._estimate_duration("p", 7, "conformal", None)
    assert isinstance(d, int) and d <= 120


def test_generate_maps_real_zerogpu_quota_grerror(monkeypatch):
    def boom(*a, **k):
        raise gr.Error("ZeroGPU quota exceeded: 240s requested vs. 30s left")
    monkeypatch.setattr(app, "_run", boom)
    with pytest.raises(gr.Error) as ei:
        app.generate("a gallery showing the same gallery", 7, "conformal")
    assert "cached example" in str(ei.value).lower()


def test_generate_passes_through_unrelated_grerror(monkeypatch):
    def boom(*a, **k):
        raise gr.Error("some unrelated validation message")
    monkeypatch.setattr(app, "_run", boom)
    with pytest.raises(gr.Error) as ei:
        app.generate("a gallery showing the same gallery", 7, "conformal")
    assert "some unrelated validation message" in str(ei.value)


def test_generate_maps_unknown_exception_to_generic(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("kernel exploded")
    monkeypatch.setattr(app, "_run", boom)
    with pytest.raises(gr.Error) as ei:
        app.generate("a gallery showing the same gallery", 7, "conformal")
    assert "failed" in str(ei.value).lower()
