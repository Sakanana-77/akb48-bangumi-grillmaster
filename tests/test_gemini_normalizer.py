import unittest

from services.srt import SrtBlock
from services.gemini.normalizer import normalize_translated_blocks


class GeminiNormalizerTests(unittest.TestCase):
    def test_removes_trailing_empty_speaker_dash_line(self):
        blocks = [
            SrtBlock(
                index=396,
                timecode="00:17:11,680 --> 00:17:13,200",
                text="- 給我適可而止。\n-",
            )
        ]

        normalized = normalize_translated_blocks(blocks)

        self.assertEqual(normalized[0].text, "- 給我適可而止。")

    def test_removes_all_empty_speaker_dash_lines(self):
        blocks = [
            SrtBlock(
                index=416,
                timecode="00:18:17,320 --> 00:18:17,860",
                text="- \n-",
            )
        ]

        normalized = normalize_translated_blocks(blocks)

        self.assertEqual(normalized[0].text, "")
        self.assertEqual(normalized[0].index, 416)
        self.assertEqual(
            normalized[0].timecode, "00:18:17,320 --> 00:18:17,860"
        )

    def test_keeps_dash_lines_with_translated_content(self):
        blocks = [
            SrtBlock(
                index=1,
                timecode="00:00:00,000 --> 00:00:01,000",
                text="- 第一人。\n- 第二人。",
            )
        ]

        normalized = normalize_translated_blocks(blocks)

        self.assertEqual(normalized[0].text, "- 第一人。\n- 第二人。")


def _space(text: str, units) -> str:
    blocks = [
        SrtBlock(
            index=1, timecode="00:00:00,000 --> 00:00:01,000", text=text
        )
    ]
    return normalize_translated_blocks(blocks, units)[0].text


class LatinNameSpacingTests(unittest.TestCase):
    def test_spaces_mixed_unit_against_han(self):
        self.assertEqual(
            _space("以及空前Meteor的茶屋。", ["空前Meteor"]),
            "以及 空前Meteor 的茶屋。",
        )

    def test_preserves_mapping_internal_spaces(self):
        self.assertEqual(
            _space("他是Long Coat Daddy啦", ["Long Coat Daddy"]),
            "他是 Long Coat Daddy 啦",
        )

    def test_no_space_against_punctuation(self):
        self.assertEqual(
            _space("那是水川Katamari？", ["水川Katamari"]),
            "那是 水川Katamari？",
        )
        self.assertEqual(_space("是Diane。", ["Diane"]), "是 Diane。")
        self.assertEqual(_space("是Diane.", ["Diane"]), "是 Diane.")

    def test_no_padding_at_line_edges(self):
        self.assertEqual(
            _space("Diane 的 Yusuke。", ["Diane", "Yusuke"]),
            "Diane 的 Yusuke。",
        )
        self.assertEqual(
            _space("那是水川Katamari", ["水川Katamari"]),
            "那是 水川Katamari",
        )

    def test_collapses_existing_extra_spaces(self):
        self.assertEqual(
            _space("原田竟然比  水川Katamari  還心動", ["水川Katamari"]),
            "原田竟然比 水川Katamari 還心動",
        )

    def test_does_not_touch_pure_han_names(self):
        self.assertEqual(_space("鎌鼬的山內", ["Diane"]), "鎌鼬的山內")

    def test_per_line_and_second_line_start(self):
        self.assertEqual(
            _space("原田竟然比\n水川Katamari還讓人心動？", ["水川Katamari"]),
            "原田竟然比\n水川Katamari 還讓人心動？",
        )

    def test_no_units_is_identity(self):
        self.assertEqual(
            _space("以及空前Meteor的茶屋。", []),
            "以及空前Meteor的茶屋。",
        )

    def test_longest_unit_wins(self):
        units = ["Diane", "Diane津田"]
        self.assertEqual(
            _space("是Diane津田。", units), "是 Diane津田。"
        )
        self.assertEqual(_space("是Diane的。", units), "是 Diane 的。")

    def test_dash_removal_then_spacing_compose(self):
        self.assertEqual(_space("-\n是Diane。", ["Diane"]), "是 Diane。")


if __name__ == "__main__":
    unittest.main()
