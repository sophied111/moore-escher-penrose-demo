"""Lightweight prompt denylist, checked before any GPU work so rejects cost no quota."""
from __future__ import annotations

import re

import gradio as gr

# Minimal, word-bounded denylist. Expand as needed; keep it conservative.
_DENY = {
    "nsfw", "porn", "pornographic", "explicit sexual", "child",
    "cp", "gore", "beheading",
}
_PATTERNS = [re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE) for term in _DENY]


def check(prompt: str) -> None:
    """Raise ``gr.Error`` on an empty/whitespace prompt or a denylist hit."""
    if not prompt or not prompt.strip():
        raise gr.Error("Please enter a prompt.")
    for pat in _PATTERNS:
        if pat.search(prompt):
            raise gr.Error("This prompt isn't allowed. Try a different scene.")
