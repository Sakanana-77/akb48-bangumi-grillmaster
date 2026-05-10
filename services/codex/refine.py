"""Codex-driven Traditional Chinese subtitle refinement."""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from project import Project
from services.srt import SrtBlock, parse_srt
from .client import run_codex_exec


_PROMPT = (Path(__file__).parent / "prompts" / "refine.md").read_text(
    encoding="utf-8"
)


class RefinementValidationError(RuntimeError):
    """Raised when the refined SRT structurally diverges from the source."""


def _parse_srt(path: Path) -> list[SrtBlock]:
    # utf-8-sig tolerates a UTF-8 BOM that Codex sometimes writes.
    raw = path.read_text(encoding="utf-8-sig").strip()
    return parse_srt(raw) if raw else []


def _validate_refined_srt(source: Path, refined: Path) -> list[str]:
    src_blocks = _parse_srt(source)
    ref_blocks = _parse_srt(refined)
    errors: list[str] = []

    if len(src_blocks) != len(ref_blocks):
        errors.append(
            f"block count differs: source={len(src_blocks)} refined={len(ref_blocks)}"
        )

    for position, (left, right) in enumerate(
        zip(src_blocks, ref_blocks), start=1
    ):
        if left.index != right.index:
            errors.append(
                f"position {position}: index changed {left.index} -> {right.index}"
            )
        if left.timecode != right.timecode:
            errors.append(
                f"block {left.index}: timecode changed "
                f"{left.timecode!r} -> {right.timecode!r}"
            )
        if not right.text:
            errors.append(f"block {right.index}: refined text is empty")

    return errors


def refine_subtitles(project: Project) -> None:
    """Run Codex refinement and structurally validate the output."""
    if project.refined_srt_path.exists():
        logger.info(
            f"Refined SRT already exists, skipping Codex invocation: "
            f"{project.refined_srt_path}"
        )
        return

    if not project.translated_path.exists():
        raise RefinementValidationError(
            f"translated SRT missing before refinement: {project.translated_path}"
        )

    project.refine_cache_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Invoking Codex for subtitle refinement: {project.id}")
    run_codex_exec(prompt=_PROMPT, cwd=project.project_path)

    if not project.refined_srt_path.exists():
        raise RefinementValidationError(
            f"Codex did not produce refined SRT: {project.refined_srt_path}"
        )

    errors = _validate_refined_srt(
        project.translated_path, project.refined_srt_path
    )
    if errors:
        raise RefinementValidationError(
            "refined SRT failed structural validation:\n" + "\n".join(errors)
        )

    logger.info(
        f"Refined SRT validated: "
        f"{len(_parse_srt(project.refined_srt_path))} blocks"
    )

    if not project.refine_report_path.exists():
        logger.warning(
            f"Refinement report missing (expected at "
            f"{project.refine_report_path})"
        )
