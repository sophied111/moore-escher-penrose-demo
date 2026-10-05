"""Moore–Escher–Penrose — public ZeroGPU Gradio demo."""
import spaces  # MUST be first: monkey-patches torch.cuda before any CUDA import

import os
import time
import traceback

import gradio as gr

import examples
import safety

_SKIP_BACKBONE = os.environ.get("ESCHER_DEMO_SKIP_BACKBONE") == "1"

# --- config + backbone, built once at module scope (ZeroGPU requirement) -------
if not _SKIP_BACKBONE:
    from escher.config import load_preset
    from escher.backbones.flux import FluxBackbone
    from escher.sampler import sample

    # escher >= v0.1.1 ships presets as package data; load by bare name.
    BASE = load_preset("flux_conformal")
    BACKBONE = FluxBackbone(model_id=BASE.model_id, num_inference_steps=BASE.num_steps)
else:  # test mode: no model, no GPU
    BASE = None
    BACKBONE = None
    sample = None


def _coerce_seed(value) -> int:
    """Coerce arbitrary input to a valid seed in [0, 2**32); raise gr.Error on garbage."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise gr.Error("Seed must be a whole number.")
    return n % (2**32)


def _friendly_zerogpu_error(exc: Exception) -> gr.Error:
    """Map a raw ZeroGPU quota/duration exception to a visitor-friendly gr.Error."""
    msg = str(exc).lower()
    if "quota" in msg:
        return gr.Error(
            "You've used your ZeroGPU quota for now. This is a heavy, full-quality "
            "run — sign in or go PRO for more GPU time, or open a cached example below."
        )
    if "illegal duration" in msg:
        return gr.Error(
            "This full-quality run is longer than your account's per-call GPU limit. "
            "Sign in / go PRO for a higher limit, or open a cached example below."
        )
    return gr.Error("Generation failed on the GPU. Please try again.")


def _is_zerogpu_limit(exc: Exception) -> bool:
    """True if the exception is a ZeroGPU quota / per-call-duration rejection."""
    msg = str(exc).lower()
    return "quota" in msg or "illegal duration" in msg


def _estimate_duration(prompt, seed, family, progress) -> int:
    """Declared ZeroGPU duration (seconds), invoked by @spaces.GPU with _run's args.

    Must accept the same arguments as _run — ZeroGPU calls the duration callable
    with the decorated function's args. Set the value from the Task 7 baseline.
    """
    return 120  # free-tier per-call cap; bump once on PRO/dedicated hardware


@spaces.GPU(duration=_estimate_duration)
def _run(prompt: str, seed: int, family: str, progress):
    """GPU body: run the braided sampler on the verbatim preset."""
    cfg = BASE.overrides(prompt=prompt, seed=seed, family=family)
    progress(0.0, desc="denoising…")
    img = sample(
        BACKBONE, cfg.prompt,
        family=cfg.family, inset_scale=cfg.inset_scale, periods=cfg.periods,
        sigma_hi=cfg.sigma_hi, sigma_lo=cfg.sigma_lo, n_ops=cfg.n_ops,
        op_gap=cfg.op_gap, warmup_sigma=cfg.warmup_sigma, focus=cfg.focus,
        upres=cfg.upres, zoom=cfg.zoom, supersample=cfg.supersample,
        time_travel=cfg.time_travel, seed=cfg.seed, size=cfg.size,
        cfg_scale=cfg.cfg_scale, family_params=cfg.family_params,
    )
    progress(1.0, desc="done")
    return img


def generate(prompt: str, seed, family: str, progress=gr.Progress()):
    """Generate a recursive Droste image from a prompt, seed, and transform family."""
    safety.check(prompt)                 # before GPU entry → rejects cost no quota
    seed = _coerce_seed(seed)
    t0 = time.time()
    try:
        img = _run(prompt, seed, family, progress)
    except gr.Error as err:
        # ZeroGPU quota/duration rejections ARE gr.Error (raised synchronously in
        # the main process from the scheduler); remap those to friendly guidance.
        # Any other gr.Error (e.g. a validation message) passes through unchanged.
        if _is_zerogpu_limit(err):
            raise _friendly_zerogpu_error(err)
        raise
    except Exception as exc:  # genuine worker failure — log server-side, show generic
        traceback.print_exc()
        raise _friendly_zerogpu_error(exc)
    caption = f"seed={seed} · family={family} · {time.time() - t0:.0f}s"
    return img, caption


with gr.Blocks(title="Moore–Escher–Penrose") as demo:
    gr.Markdown(
        "# Moore, Escher, Penrose\n"
        "Recursive Droste images from a frozen FLUX.1-dev backbone. "
        "Describe a scene that **contains a copy of itself** (a gallery whose wall "
        "shows the same gallery; a map depicting the table it lies on)."
    )
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(
                label="Prompt", lines=3,
                placeholder="a photorealistic gallery whose far wall is a photo of the same gallery, no text",
            )
            with gr.Row():
                seed = gr.Number(label="Seed", value=7, precision=0)
                randomize = gr.Button("🎲", scale=0)
            family = gr.Dropdown(
                label="Family", choices=examples.FAMILIES, value="conformal",
            )
            go = gr.Button("Generate", variant="primary")
        with gr.Column():
            out_image = gr.Image(label="Result")
            out_caption = gr.Markdown()

    gr.Examples(
        examples=examples.EXAMPLES,
        inputs=[prompt, seed, family],
        outputs=[out_image, out_caption],
        fn=generate,
        cache_examples=True,
        cache_mode="lazy",
    )

    with gr.Accordion("About / the recipe", open=False):
        gr.Markdown(
            "This demo runs the paper's `flux_conformal` preset verbatim: 128 steps, "
            "Real-ESRGAN ×4 super-resolution, matched T/T† operator window, and a "
            "post-loop time-travel refinement. Only the prompt, seed, and family vary. "
            "Method and code: https://github.com/sophied111/moore-escher-penrose"
        )

    randomize.click(lambda: int.from_bytes(os.urandom(4), "big"), outputs=seed)
    go.click(generate, inputs=[prompt, seed, family], outputs=[out_image, out_caption])

if __name__ == "__main__":
    demo.launch(mcp_server=True)
