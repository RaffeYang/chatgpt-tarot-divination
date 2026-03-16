from fastapi import HTTPException
from src.models import DivinationBody
from .base import DivinationFactory

FORTUNE_PROMPT = (
    "你是一位综合命理咨询顾问，请基于用户问题给出结构化的“AI算命”报告。"
    "你可参考塔罗、八字、姓名学、易学等常见命理思路做综合分析，但必须保持理性和边界。\n\n"
    "【方法约束】\n"
    "1. 先识别问题类型（事业/财务/感情/家庭/学习/健康作息）。\n"
    "2. 采用“趋势判断”而非“绝对预言”，避免宿命化表达。\n"
    "3. 输出必须具体可执行，不得只给空泛安慰。\n"
    "4. 不提供医疗、法律、投资确定性结论。\n\n"
    "【输出结构】\n"
    "一、问题画像（1-2句）\n"
    "二、当前运势主轴（优势/阻力/转机）\n"
    "三、三阶段趋势\n"
    "- 近期（30天）\n"
    "- 中期（3个月）\n"
    "- 远期（1年）\n"
    "四、行动建议\n"
    "- 立刻可做2条\n"
    "- 本周可做2条\n"
    "- 本月可做2条\n"
    "五、风险预警\n"
    "- 2条“需要避免的决策模式”\n"
    "六、结论\n"
    "- 3-5句总结，给出优先级最高的一件事。"
)


class FortuneFactory(DivinationFactory):

    divination_type = "fortune"

    def build_prompt(self, divination_body: DivinationBody) -> tuple[str, str]:
        prompt = divination_body.prompt.strip()
        if len(prompt) < 2:
            raise HTTPException(status_code=400, detail="Prompt too short")
        if len(prompt) > 300:
            raise HTTPException(status_code=400, detail="Prompt too long")
        return prompt, FORTUNE_PROMPT
