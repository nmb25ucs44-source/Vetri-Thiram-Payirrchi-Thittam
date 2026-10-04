import os
from pathlib import Path
from typing import List

import torch
from diffusers import DiffusionPipeline


BASE_DIR = Path(__file__).resolve().parent.parent.parent

OUTPUT_DIR = (
    BASE_DIR
    / "static"
    / "panels"
)

_pipeline = None


def get_device():
    configured = os.getenv(
        "SD_DEVICE",
        "auto",
    ).lower()

    if configured != "auto":
        return configured

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def get_pipeline():
    global _pipeline

    if _pipeline is not None:
        return _pipeline

    model_id = os.getenv(
        "SD_MODEL_ID",
        "stable-diffusion-v1-5/stable-diffusion-v1-5",
    )

    device = get_device()

    token = os.getenv("HF_TOKEN") or None

    _pipeline = DiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=(
            torch.float16
            if device == "cuda"
            else torch.float32
        ),
        token=token,
    )

    _pipeline = _pipeline.to(device)

    if device == "cuda":
        try:
            _pipeline.enable_attention_slicing()
        except Exception:
            pass

    return _pipeline


def generate_single_image(
    prompt: str,
    filename: str,
):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    pipe = get_pipeline()

    width = int(
        os.getenv(
            "SD_WIDTH",
            "512",
        )
    )

    height = int(
        os.getenv(
            "SD_HEIGHT",
            "512",
        )
    )

    steps = int(
        os.getenv(
            "SD_STEPS",
            "25",
        )
    )

    guidance = float(
        os.getenv(
            "SD_GUIDANCE",
            "7.5",
        )
    )

    full_prompt = (
        "comic book illustration, "
        "clear characters, expressive faces, "
        "cinematic composition, clean line art, "
        "detailed background, vibrant storytelling, "
        f"{prompt}"
    )

    result = pipe(
        prompt=full_prompt,
        width=width,
        height=height,
        num_inference_steps=steps,
        guidance_scale=guidance,
    )

    image = result.images[0]

    output_path = OUTPUT_DIR / filename

    image.save(output_path)

    return str(
        output_path.relative_to(BASE_DIR)
    ).replace("\\", "/")


def generate_images(panels: List):
    results = []

    for index, panel in enumerate(
        panels,
        start=1,
    ):
        if hasattr(
            panel,
            "image_prompt",
        ):
            prompt = panel.image_prompt
        else:
            prompt = panel.get(
                "image_prompt",
                "",
            )

        filename = (
            f"panel_{index}.png"
        )

        path = generate_single_image(
            prompt,
            filename,
        )

        results.append(path)

    return results