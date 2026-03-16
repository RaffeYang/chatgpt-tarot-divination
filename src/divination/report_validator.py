from typing import List


TAROT_REQUIRED_SECTIONS = [
    ("问题聚焦", ["问题聚焦"]),
    ("抽牌结果", ["抽牌结果"]),
    ("逐牌专业解读", ["逐牌专业解读", "逐牌解读"]),
    ("行动建议", ["行动建议"]),
    ("风险预警", ["风险预警"]),
    ("结论摘要", ["结论摘要"]),
]


def find_missing_tarot_sections(text: str) -> List[str]:
    missing: List[str] = []
    for section_name, keywords in TAROT_REQUIRED_SECTIONS:
        if not any(keyword in text for keyword in keywords):
            missing.append(section_name)
    return missing
