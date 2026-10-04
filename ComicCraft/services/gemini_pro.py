import os

from google import genai
from google.genai import types

from app.models import (
    OutlineResponse,
    StoryResponse,
)


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    return genai.Client(
        api_key=api_key
    )


def generate_story(
    user_prompt: str,
    outline: OutlineResponse,
) -> StoryResponse:

    client = get_client()

    model_name = os.getenv(
        "GEMINI_STORY_MODEL",
        "gemini-2.5-flash",
    )

    outline_text = outline.model_dump_json(
        indent=2
    )

    instruction = f"""
You are a professional comic script writer.

Create a complete five-panel comic script.

USER IDEA:
{user_prompt}

OUTLINE:
{outline_text}

Requirements:

1. Keep exactly five panels.
2. Keep the story consistent with the outline.
3. Each panel must contain:
   - panel_number
   - narration
   - dialogue
   - image_prompt
4. Dialogue should be short enough to fit inside
   a comic speech bubble.
5. Image prompts must clearly describe:
   - characters
   - setting
   - action
   - mood
   - visual style
6. Do not include unsafe or explicit content.
"""

    response = client.models.generate_content(
        model=model_name,
        contents=instruction,
        config=types.GenerateContentConfig(
            temperature=0.9,
            response_mime_type="application/json",
            response_schema=StoryResponse,
        ),
    )

    if not response.parsed:
        raise RuntimeError(
            "Gemini did not return a valid comic story."
        )

    return response.parsed