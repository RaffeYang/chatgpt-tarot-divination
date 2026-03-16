import json
import datetime
from typing import Optional
from anthropic import AsyncAnthropic
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI

import logging

from fastapi import Depends, HTTPException, Request, status


from src.config import settings
from fastapi import APIRouter

from src.models import DivinationBody, User
from src.user import get_user
from src.limiter import get_real_ipaddr, check_rate_limit
from src.divination import DivinationFactory
from src.divination.report_validator import find_missing_tarot_sections


def _normalize_openai_base_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    if not normalized:
        return normalized
    if normalized.endswith("/v1"):
        return normalized
    if "anthropic" in normalized:
        return normalized
    if any(k in normalized for k in ["openai.com", "minimaxi", "moonshot", "deepseek"]):
        return f"{normalized}/v1"
    return normalized


def _is_anthropic_base_url(base_url: str) -> bool:
    return "/anthropic" in (base_url or "").lower()


def _resolve_provider(explicit_protocol: Optional[str], base_url: str, model: str) -> str:
    protocol = (explicit_protocol or "").strip().lower()
    if protocol in {"anthropic", "openai"}:
        return protocol

    normalized_base_url = (base_url or "").lower()
    normalized_model = (model or "").lower()
    if "/anthropic" in normalized_base_url or "anthropic" in normalized_base_url:
        return "anthropic"
    if "minimaxi.com" in normalized_base_url and normalized_model.startswith("minimax-"):
        return "anthropic"
    if normalized_model.startswith("claude-"):
        return "anthropic"
    return "openai"


openai_client = AsyncOpenAI(
    api_key=settings.api_key,
    base_url=_normalize_openai_base_url(settings.api_base)
)
anthropic_client = AsyncAnthropic(
    api_key=settings.api_key,
    base_url=settings.api_base.rstrip("/")
)
router = APIRouter()
_logger = logging.getLogger(__name__)
STOP_WORDS = [
    "忽略", "ignore", "指令", "命令", "command", "help", "帮助", "之前",
    "幫助", "現在", "開始", "开始", "start", "restart", "重新开始", "重新開始",
    "遵守", "遵循", "遵从", "遵從"
]


def _build_runtime_system_prompt(base_system_prompt: str) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    runtime_rule = (
        f"【运行时上下文】当前系统时间为 {now}。\n"
        "若用户问题涉及“近期/未来”时间判断，请以该时间为基准。\n"
        "若用户信息不足（如缺少出生信息、对象背景、关键上下文），请明确写出“以下为基于有限信息的趋势分析”，"
        "并避免把假设写成事实。"
    )
    return f"{runtime_rule}\n\n{base_system_prompt}"


@router.post("/api/divination")
async def divination(
        request: Request,
        divination_body: DivinationBody,
        user: Optional[User] = Depends(get_user)
):

    real_ip = get_real_ipaddr(request)
    # rate limit when not login
    if settings.enable_rate_limit:
        if not user:
            max_reqs, time_window_seconds = settings.rate_limit
            check_rate_limit(f"{settings.project_name}:{real_ip}", time_window_seconds, max_reqs)
        else:
            max_reqs, time_window_seconds = settings.user_rate_limit
            check_rate_limit(
                f"{settings.project_name}:{user.login_type}:{user.user_name}", time_window_seconds, max_reqs
            )

    _logger.info(
        f"Request from {real_ip}, "
        f"user={user.model_dump_json(context=dict(ensure_ascii=False)) if user else None}, "
        f"body={divination_body.model_dump_json(context=dict(ensure_ascii=False))}"
    )
    if any(w in divination_body.prompt.lower() for w in STOP_WORDS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Prompt contains stop words"
        )
    divination_obj = DivinationFactory.get(divination_body.prompt_type)
    if not divination_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No prompt type {divination_body.prompt_type} not supported"
        )
    prompt, base_system_prompt = divination_obj.build_prompt(divination_body)
    system_prompt = _build_runtime_system_prompt(base_system_prompt)

    # custom api key, model and base url support
    custom_base_url = request.headers.get("x-api-url")
    custom_api_key = request.headers.get("x-api-key")
    custom_api_model = request.headers.get("x-api-model")
    custom_api_protocol = request.headers.get("x-api-protocol")
    api_model = custom_api_model if custom_api_model else settings.model
    effective_base_url = (custom_base_url or settings.api_base or "").strip().rstrip("/")
    effective_api_key = custom_api_key or settings.api_key

    if not effective_base_url or not effective_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="请设置 API KEY 和 API BASE URL"
        )

    provider = _resolve_provider(custom_api_protocol, effective_base_url, api_model)

    try:
        if provider == "anthropic":
            api_client = (
                anthropic_client
                if not custom_api_key and not custom_base_url
                else AsyncAnthropic(api_key=effective_api_key, base_url=effective_base_url)
            )
            llm_stream = await api_client.messages.create(
                model=api_model,
                max_tokens=1400,
                temperature=0.6,
                system=system_prompt,
                stream=True,
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }]
            )
        else:
            normalized_effective_base_url = _normalize_openai_base_url(effective_base_url)
            api_client = (
                openai_client
                if not custom_api_key and not custom_base_url
                else AsyncOpenAI(api_key=effective_api_key, base_url=normalized_effective_base_url)
            )
            llm_stream = await api_client.chat.completions.create(
                model=api_model,
                max_tokens=1400,
                temperature=0.6,
                top_p=1,
                stream=True,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {"role": "user", "content": prompt}
                ]
            )
    except Exception as e:
        # Fallback: some Anthropic-compatible gateways may not expose /anthropic in URL.
        should_fallback_to_anthropic = (
            provider == "openai"
            and "minimaxi" in effective_base_url.lower()
            and getattr(e, "status_code", None) in {400, 404, 415}
        )
        if should_fallback_to_anthropic:
            try:
                fallback_client = AsyncAnthropic(api_key=effective_api_key, base_url=effective_base_url)
                llm_stream = await fallback_client.messages.create(
                    model=api_model,
                    max_tokens=1400,
                    temperature=0.6,
                    system=system_prompt,
                    stream=True,
                    messages=[{
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}]
                    }]
                )
                provider = "anthropic"
            except Exception as fallback_error:
                _logger.error(f"LLM API error: {fallback_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"LLM API error: {str(fallback_error)}"
                ) from fallback_error
        else:
            _logger.error(f"LLM API error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"LLM API error: {str(e)}"
            ) from e

    async def get_stream_generator():
        full_text = ""
        try:
            if provider == "anthropic":
                async for event in llm_stream:
                    if (
                        getattr(event, "type", "") == "content_block_delta"
                        and getattr(getattr(event, "delta", None), "type", "") == "text_delta"
                    ):
                        current_response = event.delta.text
                        if current_response:
                            full_text += current_response
                            yield f"data: {json.dumps(current_response)}\n\n"
            else:
                async for event in llm_stream:
                    if event.choices and event.choices[0].delta and event.choices[0].delta.content:
                        current_response = event.choices[0].delta.content
                        full_text += current_response
                        yield f"data: {json.dumps(current_response)}\n\n"
            if divination_body.prompt_type == "tarot":
                missing_sections = find_missing_tarot_sections(full_text)
                if missing_sections:
                    warning = (
                        "\n\n---\n⚠️ 结构化校验提醒：本次结果缺少以下章节："
                        + "、".join(missing_sections)
                        + "。建议补充后再决策。"
                    )
                    yield f"data: {json.dumps(warning)}\n\n"
        except Exception as e:
            _logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(get_stream_generator(), media_type='text/event-stream')
