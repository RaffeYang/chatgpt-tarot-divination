from fastapi import HTTPException
from src.models import DivinationBody
from .base import DivinationFactory

DREAM_PROMPT = (
    "你是一位专业的梦境解析顾问，请结合「周公解梦传统象征」与「现代心理学视角」做双轨分析。"
    "用户会给出梦境描述，请按以下结构输出：\n\n"
    "【方法约束】\n"
    "1. 先提取梦中关键意象（人物、场景、动作、情绪）。\n"
    "2. 分两部分解释：A. 传统象征解读（周公语境）B. 心理学解读（压力、未完成事件、情绪投射）。\n"
    "3. 不把梦解释成确定预言，不给医疗诊断结论。\n"
    "4. 每个结论都要回扣用户梦境细节，避免空泛模板。\n\n"
    "【输出结构】\n"
    "一、梦境摘要（1-2句）\n"
    "二、关键意象清单（3-6条）\n"
    "三、传统象征解读\n"
    "四、心理学解读\n"
    "五、现实映射（近期可能对应的压力源/关系议题）\n"
    "六、行动建议\n"
    "- 今晚可执行1条\n"
    "- 未来7天可执行2条\n"
    "七、结论摘要（3句以内）"
)


class DreamFactory(DivinationFactory):

    divination_type = "dream"

    def build_prompt(self, divination_body: DivinationBody) -> tuple[str, str]:
        prompt = divination_body.prompt.strip()
        if len(prompt) > 300:
            raise HTTPException(status_code=400, detail="Prompt too long")
        if len(prompt) < 2:
            raise HTTPException(status_code=400, detail="Prompt too short")
        prompt = f"我的梦境是: {prompt}"
        return prompt, DREAM_PROMPT
