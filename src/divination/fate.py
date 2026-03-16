from fastapi import HTTPException
from src.models import DivinationBody
from .base import DivinationFactory

SYS_PROMPT = (
    "你是一位关系匹配分析顾问。用户会提供两个人名，"
    "请做理性、尊重且中立的姻缘/关系匹配解读。\n\n"
    "【方法约束】\n"
    "1. 不根据性别、性取向、姓名真实性做歧视性结论。\n"
    "2. 不使用固定概率模板，不强行“90%合适”。\n"
    "3. 仅给出关系动力学层面的趋势判断与沟通建议，不做宿命断语。\n"
    "4. 保持尊重，避免攻击性表达。\n\n"
    "【输出结构】\n"
    "一、关系基调（1-2句）\n"
    "二、潜在吸引点（2-3条）\n"
    "三、潜在摩擦点（2-3条）\n"
    "四、相处建议\n"
    "- 立即可做2条\n"
    "- 中期改善2条\n"
    "五、风险预警（1-2条）\n"
    "六、结论（3句以内）"
)


class Fate(DivinationFactory):

    divination_type = "fate"

    def build_prompt(self, divination_body: DivinationBody) -> tuple[str, str]:
        fate = divination_body.fate
        if not fate:
            raise HTTPException(status_code=400, detail="Fate is required")
        name1 = fate.name1.strip()
        name2 = fate.name2.strip()
        if len(name1) < 1 or len(name2) < 1:
            raise HTTPException(status_code=400, detail="Name cannot be empty")
        if len(name1) > 40 or len(name2) > 40:
            raise HTTPException(status_code=400, detail="Prompt too long")
        prompt = f"{name1}, {name2}"
        return prompt, SYS_PROMPT
