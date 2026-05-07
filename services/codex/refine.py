"""Codex-driven Traditional Chinese subtitle refinement."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from project import Project
from .client import run_codex_exec


_PROMPT = (Path(__file__).parent / "prompts" / "refine.md").read_text(
    encoding="utf-8"
)
_BLOCK_SEPARATOR = re.compile(r"\n\s*\n")


class RefinementValidationError(RuntimeError):
    """Raised when the refined SRT structurally diverges from the source."""


@dataclass(frozen=True)
class _SrtBlock:
    index: int
    timecode: str
    text: str


def _parse_srt(path: Path) -> list[_SrtBlock]:
    raw = path.read_text(encoding="utf-8-sig").strip()
    if not raw:
        return []

    blocks: list[_SrtBlock] = []
    for position, chunk in enumerate(_BLOCK_SEPARATOR.split(raw), start=1):
        lines = chunk.splitlines()
        if len(lines) < 2:
            raise ValueError(f"block {position} has fewer than 2 lines")
        try:
            index = int(lines[0].strip())
        except ValueError as exc:
            raise ValueError(
                f"block {position} has invalid index: {lines[0]!r}"
            ) from exc
        timecode = lines[1].strip()
        if "-->" not in timecode:
            raise ValueError(
                f"block {index} has invalid timecode: {timecode!r}"
            )
        text = "\n".join(lines[2:]).strip()
        blocks.append(_SrtBlock(index=index, timecode=timecode, text=text))
    return blocks


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
