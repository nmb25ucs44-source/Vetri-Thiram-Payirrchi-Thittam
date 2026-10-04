import os

from google import genai
from google.genai import types

from app.models import OutlineResponse


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


def generate_outline(user_prompt: str) -> OutlineResponse:
    client = get_client()

    model_name = os.getenv(
        "GEMINI_OUTLINE_MODEL",
        "gemini-2.5-flash-lite",
    )

    instruction = f"""
You are a comic story planner.

Create a five-panel comic outline based on the
user's idea below.

USER IDEA:
{user_prompt}

Requirements:
- Exactly five panels.
- Give the comic a suitable title.
- Identify a genre.
- Each panel must have:
  panel_number
  title
  description
- Keep the story coherent from panel 1 to panel 5.
- Make each panel visually useful for image generation.
"""

    response = client.models.generate_content(
        model=model_name,
        contents=instruction,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
            response_schema=OutlineResponse,
        ),
    )

    if not response.parsed:
        raise RuntimeError(
            "Gemini did not return a valid comic outline."
        )

    return response.parsed