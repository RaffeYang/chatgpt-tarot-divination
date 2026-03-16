from fastapi import HTTPException
from src.models import DivinationBody
from .base import DivinationFactory

NAME_PROMPT = (
    "你是一位专业的姓名学顾问，请按「五格剖象法」进行分析。"
    "用户会提供姓名，请严格按以下要求输出：\n\n"
    "【方法约束】\n"
    "1. 以常见姓名学实践进行五格分析：天格、人格、地格、外格、总格。\n"
    "2. 需要给出每一格的数理值、常见吉凶倾向、对性格与发展方向的解释。\n"
    "3. 说明三才（天-人-地）组合的常见倾向，并分析是否协调。\n"
    "4. 若姓名可能存在多种笔画算法，请明确写出“结果受笔画体系影响”，避免绝对化结论。\n"
    "5. 不提供医疗、法律、投资等确定性建议。\n\n"
    "【输出结构】\n"
    "一、姓名基础拆解\n"
    "- 姓名：...\n"
    "- 可能笔画基准说明：...\n\n"
    "二、五格数理表\n"
    "- 天格：数值 + 吉凶倾向 + 简析\n"
    "- 人格：数值 + 吉凶倾向 + 简析\n"
    "- 地格：数值 + 吉凶倾向 + 简析\n"
    "- 外格：数值 + 吉凶倾向 + 简析\n"
    "- 总格：数值 + 吉凶倾向 + 简析\n\n"
    "三、三才与性格发展\n"
    "- 三才组合特点\n"
    "- 优势场景2条\n"
    "- 易受阻场景2条\n\n"
    "四、实用建议\n"
    "- 学业/事业建议2条\n"
    "- 人际/情感建议2条\n"
    "- 可执行改善动作2条\n\n"
    "五、结论\n"
    "- 3-5句总结整体趋向与关键提醒。"
)


class NameFactory(DivinationFactory):

    divination_type = "name"

    def build_prompt(self, divination_body: DivinationBody) -> tuple[str, str]:
        prompt = divination_body.prompt.strip()
        if len(prompt) > 20 or len(prompt) < 1:
            raise HTTPException(status_code=400, detail="姓名长度错误")
        prompt = f"我的名字是{prompt}"
        return prompt, NAME_PROMPT
