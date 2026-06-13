"""Command-line interface for the video captioning pipeline.

This module provides a CLI interface to submit and process online videos
for automatic captioning and translation.
"""

import typer
from typing_extensions import Annotated
from loguru import logger
from project import ProgressStage
from workflow import submit_project


app = typer.Typer(
    help="Bangumi GrillMaster - Automatic transcription and translation for Bangumi videos",
    add_completion=False,
)


@app.command()
def process(
    source_str: Annotated[
        str,
        typer.Argument(
            help="Video source, id, url, or local media path (e.g., 'BV1ZArvBaEqL', 'https://www.bilibili.com/video/BV1ZArvBaEqL', 'https://youtu.be/dQw4w9WgXcQ', 'v=dQw4w9WgXcQ', './episode.mp4').",
            show_default=False,
        ),
    ],
    translation_hint: Annotated[
        str | None,
        typer.Argument(
            help="Translation hint for the video. If not provided, uses video title.",
            show_default=False,
        ),
    ] = None,
    break_after: Annotated[
        ProgressStage | None,
        typer.Option(
            "--break-after",
            "--break",
            "-break",
            help=(
                "Stop after reaching the given workflow stage. "
                "Example: is_asr_completed."
            ),
            show_default=False,
        ),
    ] = None,
    parent_project: Annotated[
        str | None,
        typer.Option(
            "--parent-project",
            help=(
                "Path to a parent project directory whose pre_pass.json "
                "should seed this project's pre-pass for cross-episode "
                "consistency (e.g., 'projects/BV1ZArvBaEqL' or an archived "
                "path). Accepts a directory path, not an ID, since the "
                "parent project may already be archived."
            ),
            show_default=False,
        ),
    ] = None,
    source_srt: Annotated[
        str | None,
        typer.Option(
            "--source-srt",
            help=(
                "Use an external Japanese SRT as the source subtitles and "
                "skip ElevenLabs ASR/SRT generation. Video/audio are still "
                "processed as Gemini context."
            ),
            show_default=False,
        ),
    ] = None,
    refine: Annotated[
        bool,
        typer.Option(
            "--refine",
            help=(
                "Force-enable subtitle refinement stage for this run. "
                "Overrides ENABLE_SRT_REFINE setting (default off)."
            ),
        ),
    ] = False,
    glossary_check: Annotated[
        bool,
        typer.Option(
            "--glossary-check",
            help=(
                "Force-enable the fixed-glossary localization check stage "
                "for this run. Overrides ENABLE_GLOSSARY_CHECK setting "
                "(default off). Only runs if a refined SRT exists."
            ),
        ),
    ] = False,
    cover: Annotated[
        bool,
        typer.Option(
            "--cover",
            help=(
                "Force-enable async cover image generation for this run. "
                "Overrides ENABLE_COVER_GENERATION setting (default off). "
                "Skipped entirely when --break-after is also set."
            ),
        ),
    ] = False,
) -> None:
    """Submit and process an online or local video for captioning and translation.

    This command will:
    1. Create a new project with the given video source
    2. Download the video from source, or copy a local media file
    3. Extract audio and generate transcription
    4. Translate subtitles to target language

    Examples:
        # Process a video without translation hint
        python main.py BV1ZArvBaEqL

        # Process a video with translation hint
        python main.py BV1ZArvBaEqL "Python tutorial video"

        # Process a video with description containing spaces
        python main.py BV1ZArvBaEqL "This is a machine learning basics video"
    """
    logger.info(
        f"CLI invoked with source_str={source_str}, "
        f"translation_hint={translation_hint}, break_after={break_after}, "
        f"parent_project={parent_project}, source_srt={source_srt}, "
        f"refine={refine}, "
        f"glossary_check={glossary_check}, cover={cover}"
    )

    try:
        submit_project(
            source_str=source_str,
            translation_hint=translation_hint,
            break_after=break_after,
            parent_project_path=parent_project,
            source_srt_path=source_srt,
            enable_refine=refine,
            enable_glossary_check=glossary_check,
            enable_cover=cover,
        )
        logger.success(f"Successfully completed processing for {source_str}")
    except Exception as e:
        logger.error(f"Failed to process video {source_str}: {e}")
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
