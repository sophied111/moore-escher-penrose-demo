import gradio as gr
import pytest

import safety


def test_clean_prompt_passes():
    safety.check("a gallery whose far wall is a photo of the same gallery")


def test_empty_prompt_rejected():
    with pytest.raises(gr.Error):
        safety.check("   ")


def test_denylisted_term_rejected():
    with pytest.raises(gr.Error):
        safety.check("a NSFW scene")


def test_denylist_is_case_insensitive_and_word_bounded():
    with pytest.raises(gr.Error):
        safety.check("NsFw gallery")
    # substring inside an ordinary word must NOT trip the filter:
    safety.check("a classic Scunthorpe railway station")
