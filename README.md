---
title: Moore–Escher–Penrose
emoji: ♾️
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 6.29.1
app_file: app.py
python_version: "3.12"
short_description: Recursive Droste images from a frozen diffusion model
startup_duration_timeout: 1h
---

# Moore, Escher, Penrose — A Conformal Golden Braid

Generate recursive Print-Gallery / Droste images with a frozen FLUX.1-dev
backbone and no fine-tuning. Type a self-referential prompt (the scene should
contain a copy of itself), pick a seed and a transform family, and generate.

Paper method and code: https://github.com/sophied111/moore-escher-penrose
