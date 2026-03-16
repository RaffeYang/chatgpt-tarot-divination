import unittest

from fastapi import HTTPException

from src.divination.report_validator import find_missing_tarot_sections
from src.divination.tarot import TarotFactory
from src.models import DivinationBody


class TarotQualityTest(unittest.TestCase):

    def test_tarot_prompt_too_short(self):
        with self.assertRaises(HTTPException):
            TarotFactory().build_prompt(DivinationBody(prompt="a", prompt_type="tarot"))

    def test_tarot_prompt_too_long(self):
        with self.assertRaises(HTTPException):
            TarotFactory().build_prompt(
                DivinationBody(prompt="x" * 201, prompt_type="tarot")
            )

    def test_tarot_prompt_valid(self):
        prompt, _ = TarotFactory().build_prompt(
            DivinationBody(prompt="我最近换工作是否合适？", prompt_type="tarot")
        )
        self.assertEqual(prompt, "我最近换工作是否合适？")

    def test_tarot_report_validator(self):
        complete_report = (
            "一、问题聚焦\n"
            "二、抽牌结果\n"
            "三、逐牌专业解读\n"
            "五、行动建议\n"
        )
        self.assertEqual(find_missing_tarot_sections(complete_report), [])

        missing = find_missing_tarot_sections("一、问题聚焦\n二、抽牌结果\n")
        self.assertIn("逐牌专业解读", missing)
        self.assertIn("行动建议", missing)


if __name__ == "__main__":
    unittest.main()
