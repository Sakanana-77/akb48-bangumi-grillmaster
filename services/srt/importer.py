"""Import external SRT files into the project SRT shape."""

from pathlib import Path

from loguru import logger

from .io import parse_srt, serialize_srt


def import_srt_file(input_path: str | Path, output_path: str | Path) -> None:
    """Validate, reindex, and copy an external SRT file.

    This is used for OCR/hard-subtitle workflows where the source Japanese SRT
    is produced outside this project but should continue through the existing
    Gemini translation and finalize stages.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Source SRT file not found: {input_path}")

    blocks = parse_srt(input_path.read_text(encoding="utf-8-sig"))
    if not blocks:
        raise ValueError(f"Source SRT file has no subtitle blocks: {input_path}")

    reindexed = [
        block.model_copy(update={"index": index})
        for index, block in enumerate(blocks, start=1)
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialize_srt(reindexed), encoding="utf-8")
    logger.success(f"Imported source SRT: {input_path} -> {output_path}")
