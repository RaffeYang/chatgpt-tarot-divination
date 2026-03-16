import datetime
from fastapi import HTTPException
from src.models import DivinationBody
from .base import DivinationFactory

NEW_NAME_PROMPT = (
    "你是一位专业中文起名顾问，请综合音形义、五行平衡倾向、书写与传播性进行起名。"
    "用户会提供姓氏、生日、性别和偏好，请按以下结构输出：\n\n"
    "【方法约束】\n"
    "1. 名字需符合中文命名习惯，避免生僻到难以识读。\n"
    "2. 结合生日信息给出五行补益“倾向”说明，不做绝对断语。\n"
    "3. 解释每个名字的字义、读音、整体气质与适配场景。\n"
    "4. 给出避用字提示（歧义、谐音风险、书写复杂度等）。\n\n"
    "【输出结构】\n"
    "一、命名策略摘要（2-3句）\n"
    "二、推荐名（5个）\n"
    "- 每个名字都包含：名字、拼音、字义拆解、推荐理由、潜在注意点\n"
    "三、备选名（3个）\n"
    "四、避用建议（2-3条）\n"
    "五、最终建议（首选1个+适用理由）"
)


class NewNameFactory(DivinationFactory):

    divination_type = "new_name"

    def build_prompt(self, divination_body: DivinationBody) -> tuple[str, str]:
        if (not divination_body.new_name or not all([
            divination_body.new_name.surname,
            divination_body.new_name.birthday,
            divination_body.new_name.sex,
        ]) or len(divination_body.new_name.new_name_prompt) > 20):
            raise HTTPException(status_code=400, detail="起名参数错误")

        try:
            birthday = datetime.datetime.strptime(
                divination_body.new_name.birthday, '%Y-%m-%d %H:%M:%S'
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="Birthday format must be YYYY-MM-DD HH:MM:SS"
            ) from exc
        prompt = (
            f"姓氏是{divination_body.new_name.surname.strip()},"
            f"性别是{divination_body.new_name.sex.strip()},"
            f"生日是{birthday.year}年{birthday.month}月{birthday.day}日{birthday.hour}时{birthday.minute}分{birthday.second}秒"
        )
        if divination_body.new_name.new_name_prompt:
            prompt += f",我的要求是: {divination_body.new_name.new_name_prompt.strip()}"
        return prompt, NEW_NAME_PROMPT
