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
