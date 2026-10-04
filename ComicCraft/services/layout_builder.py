from typing import List

from app.models import (
    OutlineResponse,
    StoryResponse,
)


def build_comic(
    outline: OutlineResponse,
    story: StoryResponse,
    image_paths: List[str],
):
    panels = []

    for index in range(5):
        outline_panel = outline.panels[index]
        story_panel = story.panels[index]

        panels.append(
            {
                "panel_number": (
                    story_panel.panel_number
                ),
                "title": outline_panel.title,
                "description": (
                    outline_panel.description
                ),
                "narration": (
                    story_panel.narration
                ),
                "dialogue": (
                    story_panel.dialogue
                ),
                "image_prompt": (
                    story_panel.image_prompt
                ),
                "image_path": image_paths[index],
            }
        )

    return {
        "title": story.title,
        "genre": outline.genre,
        "panels": panels,
    }