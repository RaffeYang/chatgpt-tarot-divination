from fastapi import HTTPException
from src.models import DivinationBody
from .base import DivinationFactory

SYS_PROMPT = (
    "你是一位专业梅花易数分析师。用户将提供两个数字，"
    "请依据常见“数起卦”规则给出结构化分析。\n\n"
    "【方法约束】\n"
    "1. 按常见规则说明取卦步骤：数字取象、上卦/下卦、动爻判定（若规则存在分支请说明采用哪一套）。\n"
    "2. 输出本卦、互卦、变卦（若可推导），并解释卦象关系。\n"
    "3. 解释时结合象、数、理，不只给结论。\n"
    "4. 不做绝对预言，不给医疗/法律/投资确定性建议。\n\n"
    "【输出结构】\n"
    "一、起卦过程\n"
    "二、卦象结果（本卦/互卦/变卦）\n"
    "三、卦义解读（当前态势、主要矛盾、潜在转机）\n"
    "四、时间与节奏提示（近期/中期）\n"
    "五、行动建议（短期2条，中期2条）\n"
    "六、结论（3句以内）"
)


class PlumFlowerFactory(DivinationFactory):

    divination_type = "plum_flower"

    def build_prompt(self, divination_body: DivinationBody) -> tuple[str, str]:
        if not divination_body.plum_flower:
            raise HTTPException(status_code=400, detail="No plum_flower")
        num1 = divination_body.plum_flower.num1
        num2 = divination_body.plum_flower.num2
        if num1 <= 0 or num2 <= 0:
            raise HTTPException(status_code=400, detail="Numbers must be positive")
        prompt = f"我选择的数字是: {num1} 和 {num2}"
        return prompt, SYS_PROMPT
