import datetime
from fastapi import HTTPException
from src.models import DivinationBody
from .base import DivinationFactory

BIRTHDAY_PROMPT = (
    "你是一位专业八字命理分析顾问，请以四柱八字的常见分析路径输出报告。"
    "用户会提供公历出生时间，请按以下结构输出，强调“趋势判断而非宿命论”：\n\n"
    "【方法约束】\n"
    "1. 先给出四柱（年柱/月柱/日柱/时柱）并解释日主。\n"
    "2. 给出五行强弱倾向、寒暖燥湿与平衡思路。\n"
    "3. 分析十神结构时，明确“倾向”而非绝对断语。\n"
    "4. 输出包含事业、财务、关系、学习成长、健康作息五个维度。\n"
    "5. 不提供医疗、法律、投资确定性结论。\n\n"
    "【输出结构】\n"
    "一、命盘基础\n"
    "- 四柱与日主\n"
    "- 五行总体分布与偏旺偏弱\n\n"
    "二、核心格局与性格倾向\n"
    "三、五维运势评估\n"
    "- 事业\n"
    "- 财务\n"
    "- 关系\n"
    "- 学习成长\n"
    "- 健康作息\n\n"
    "四、阶段性建议\n"
    "- 近期（1-3个月）2条\n"
    "- 中期（6-12个月）2条\n\n"
    "五、风险提醒\n"
    "- 2条“应避免的行为模式”\n\n"
    "六、总结\n"
    "- 3-5句结论，给出优先行动顺序。"
)


class BirthdayFactory(DivinationFactory):

    divination_type = "birthday"

    def build_prompt(self, divination_body: DivinationBody) -> tuple[str, str]:
        if not divination_body.birthday:
            raise HTTPException(status_code=400, detail="Birthday is required")
        return self.internal_build_prompt(divination_body.birthday)

    def internal_build_prompt(self, birthday: str) -> tuple[str, str]:
        try:
            birthday = datetime.datetime.strptime(
                birthday, '%Y-%m-%d %H:%M:%S'
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="Birthday format must be YYYY-MM-DD HH:MM:SS"
            ) from exc
        prompt = f"我的生日是{birthday.year}年{birthday.month}月{birthday.day}日{birthday.hour}时{birthday.minute}分{birthday.second}秒"
        return prompt, BIRTHDAY_PROMPT
