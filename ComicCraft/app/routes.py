import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models import PromptRequest
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_images
from app.services.layout_builder import build_comic
from app.services.exporters import export_comic_pdf


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": "ComicCraft",
        },
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
):
    try:
        prompt_request = PromptRequest(prompt=prompt)

        outline = generate_outline(
            prompt_request.prompt
        )

        story = generate_story(
            prompt_request.prompt,
            outline,
        )

        image_paths = generate_images(
            story.panels
        )

        comic = build_comic(
            outline,
            story,
            image_paths,
        )

        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,
                "comic": comic,
            },
        )

    except Exception as exc:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": str(exc),
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_comic_json(data: PromptRequest):
    outline = generate_outline(data.prompt)

    story = generate_story(
        data.prompt,
        outline,
    )

    image_paths = generate_images(
        story.panels
    )

    comic = build_comic(
        outline,
        story,
        image_paths,
    )

    return comic


@router.post("/test-image")
async def test_image(data: PromptRequest):
    image_paths = generate_images(
        [
            {
                "panel_number": 1,
                "image_prompt": data.prompt,
                "narration": "",
                "dialogue": "",
            }
        ]
    )

    return {
        "success": True,
        "images": image_paths,
    }


@router.post("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse(
        "export_success.html",
        {
            "request": request,
        },
    )


@router.get("/download/{filename}")
async def download_file(filename: str):
    export_dir = BASE_DIR / "static" / "exports"

    safe_filename = Path(filename).name

    file_path = export_dir / safe_filename

    if not file_path.exists():
        return {
            "error": "File not found"
        }

    return FileResponse(
        path=file_path,
        filename=safe_filename,
        media_type="application/pdf",
    )