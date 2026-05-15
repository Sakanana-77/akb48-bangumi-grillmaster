"""Post-translation SRT normalization helpers."""

import re
from collections.abc import Callable, Iterable

from services.srt import SrtBlock

# Characters that must be separated from a Latin-containing name unit by one
# half-width space (Han + kana letters only). CJK punctuation, the middle dot
# (U+30FB), the choonpu (U+30FC), full-width forms, ASCII punctuation and
# whitespace are deliberately excluded so the unit hugs punctuation/line edges.
_CJK_RE = re.compile(
    r"[ぁ-ゖァ-ヺ㐀-䶿一-鿿豈-﫿]"
)
_HAS_LATIN_RE = re.compile(r"[A-Za-z]")


def normalize_translated_blocks(
    blocks: list[SrtBlock], latin_name_units: Iterable[str] = ()
) -> list[SrtBlock]:
    """Normalize translated block text without changing timing metadata.

    `latin_name_units` are agreed proper-noun renderings (from the pre-pass
    briefing) that contain Latin letters. Each is treated as one indivisible
    unit and gets exactly one half-width space against adjacent Han/kana,
    matching the Netflix spacing convention deterministically instead of
    relying on the translator to apply it per block.
    """
    space_latin_names = _build_latin_name_spacer(latin_name_units)
    return [
        SrtBlock(
            index=block.index,
            timecode=block.timecode,
            text=space_latin_names(_remove_empty_speaker_dash_lines(block.text)),
        )
        for block in blocks
    ]


def _remove_empty_speaker_dash_lines(text: str) -> str:
    """Remove speaker-marker lines that contain only a dash."""
    return "\n".join(
        line for line in text.splitlines() if line.strip() != "-"
    )


def _build_latin_name_spacer(
    latin_name_units: Iterable[str],
) -> Callable[[str], str]:
    """Compile a per-line spacer for the given Latin-containing name units.

    Returns the identity function when there are no usable units so callers
    (and existing tests) that pass nothing keep their previous behavior.
    """
    units = sorted(
        {
            u.strip()
            for u in latin_name_units
            if u and u.strip() and _HAS_LATIN_RE.search(u)
        },
        key=len,
        reverse=True,  # longest-first so `Diane津田` wins over `Diane`
    )
    if not units:
        return lambda text: text

    alternation = "|".join(re.escape(u) for u in units)
    # The surrounding [ \t]* is consumed so pre-existing wrong/duplicated
    # boundary spaces are rewritten, not just supplemented. Limitation: two
    # distinct Latin units separated only by whitespace would merge — that
    # does not occur here (names are always split by Han/punctuation).
    pattern = re.compile(rf"[ \t]*(?P<name>{alternation})[ \t]*")

    def space_line(line: str) -> str:
        def repl(match: re.Match) -> str:
            name = match.group("name")
            before = line[match.start() - 1] if match.start() > 0 else ""
            after = line[match.end()] if match.end() < len(line) else ""
            left = " " if _CJK_RE.match(before) else ""
            right = " " if _CJK_RE.match(after) else ""
            return f"{left}{name}{right}"

        return pattern.sub(repl, line)

    def space_text(text: str) -> str:
        # Per physical line: "line start/end" means the subtitle line edge,
        # and a name is never spaced across a wrap.
        return "\n".join(space_line(line) for line in text.split("\n"))

    return space_text
