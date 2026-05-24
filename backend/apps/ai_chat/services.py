import json
import re
from dataclasses import dataclass
from datetime import date

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.ai_chat.models import (
    AIConsultationResult,
    AIConversation,
    AIMessage,
    PromptTemplate,
)
from apps.ai_chat.prompts import (
    DISCLAIMER,
    PET_HEALTH_CONSULT_PROMPT,
    PET_HEALTH_CONSULT_SCENE,
)
from apps.ai_chat.providers.base import AIProviderError
from apps.ai_chat.providers.factory import ProviderFactory
from apps.pets.models import HealthRecord, Pet

VALID_RISK_LEVELS = {"low", "medium", "high", "unknown"}


@dataclass
class ConsultationPayload:
    conversation: AIConversation
    user_message: AIMessage
    assistant_message: AIMessage
    result: AIConsultationResult
    reply: str


def get_owned_conversation(user, conversation_id):
    return get_object_or_404(
        AIConversation.objects.select_related("pet", "user"),
        id=conversation_id,
        user=user,
        status__in=[AIConversation.Status.ACTIVE, AIConversation.Status.ARCHIVED],
    )


def get_owned_pet(user, pet_id):
    return get_object_or_404(Pet, id=pet_id, owner=user)


def build_pet_context(pet):
    today = timezone.localdate()
    latest_by_type = {
        record_type: pet.health_records.filter(record_type=record_type).order_by(
            "-record_date",
            "-created_at",
        ).first()
        for record_type in [
            HealthRecord.RecordType.VACCINE,
            HealthRecord.RecordType.DEWORM,
            HealthRecord.RecordType.MEDICAL,
            HealthRecord.RecordType.ALLERGY,
        ]
    }
    latest_weights = pet.weight_records.order_by("-record_date", "-created_at")[:3]

    lines = [
        "当前咨询对象：",
        f"宠物名称：{pet.name}",
        f"物种：{pet.get_species_display()}",
        f"品种：{pet.breed or '未填写'}",
        f"性别：{pet.get_gender_display()}",
        f"年龄：{format_age(pet.birthday, today)}",
        f"体重：{pet.weight}kg" if pet.weight is not None else "体重：未填写",
        f"是否绝育：{'是' if pet.neutered else '否'}",
        f"备注：{pet.remark or '无'}",
        "",
        "健康记录摘要：",
        f"最近疫苗：{format_health_record(latest_by_type[HealthRecord.RecordType.VACCINE])}",
        f"最近驱虫：{format_health_record(latest_by_type[HealthRecord.RecordType.DEWORM])}",
        f"最近就诊：{format_health_record(latest_by_type[HealthRecord.RecordType.MEDICAL])}",
        f"过敏史：{format_health_record(latest_by_type[HealthRecord.RecordType.ALLERGY])}",
        "最近体重：" + format_weight_records(latest_weights),
    ]
    return "\n".join(lines)


def format_age(birthday, today):
    if not birthday:
        return "未填写"
    months = max(0, (today.year - birthday.year) * 12 + today.month - birthday.month)
    if today.day < birthday.day and months > 0:
        months -= 1
    return f"{months // 12}岁{months % 12}个月"


def format_health_record(record):
    if not record:
        return "暂无记录"
    extra = f"，下次提醒 {record.next_remind_date}" if record.next_remind_date else ""
    return f"{record.title}，{record.record_date}{extra}"


def format_weight_records(records):
    items = [f"{record.weight}kg（{record.record_date}）" for record in records]
    return "；".join(items) if items else "暂无记录"


def get_active_prompt():
    template = PromptTemplate.objects.filter(
        scene=PET_HEALTH_CONSULT_SCENE,
        is_active=True,
    ).first()
    return template.content if template else PET_HEALTH_CONSULT_PROMPT


def build_messages(pet, user_message, image_urls):
    context = build_pet_context(pet)
    image_text = "、".join(image_urls) if image_urls else "无"
    content = "\n".join(
        [
            context,
            "",
            "用户描述：",
            user_message,
            "",
            f"用户上传图片信息：{image_text}",
        ]
    )
    return [
        {"role": "system", "content": get_active_prompt()},
        {"role": "user", "content": content},
    ]


def consult_pet_health(user, pet_id, message, image_urls=None, conversation_id=None):
    image_urls = image_urls or []
    pet = get_owned_pet(user, pet_id)
    provider = ProviderFactory.create()

    with transaction.atomic():
        if conversation_id:
            conversation = get_owned_conversation(user, conversation_id)
            if conversation.pet_id and conversation.pet_id != pet.id:
                conversation.pet = pet
        else:
            conversation = AIConversation.objects.create(
                user=user,
                pet=pet,
                title=message[:40] or "AI 健康咨询",
                model_provider=provider.provider_name,
                model_name=getattr(provider, "model", settings.AI_MODEL),
            )

        if not conversation.model_provider:
            conversation.model_provider = provider.provider_name
        if not conversation.model_name:
            conversation.model_name = getattr(provider, "model", settings.AI_MODEL)
        conversation.pet = pet
        conversation.status = AIConversation.Status.ACTIVE
        conversation.save(update_fields=["pet", "model_provider", "model_name", "status", "updated_at"])

        user_record = AIMessage.objects.create(
            conversation=conversation,
            role=AIMessage.Role.USER,
            content=message,
            image_urls=image_urls,
        )

    messages = build_messages(pet, message, image_urls)
    reply_text = provider.chat(
        messages=messages,
        images=image_urls,
        response_format={"type": "json_object"},
    )
    result_data = normalize_result(parse_ai_json(reply_text), reply_text)
    reply = result_data["summary"]

    with transaction.atomic():
        assistant_record = AIMessage.objects.create(
            conversation=conversation,
            role=AIMessage.Role.ASSISTANT,
            content=reply_text,
            image_urls=[],
            raw_response={"parsed_result": result_data},
        )
        result = AIConsultationResult.objects.create(
            conversation=conversation,
            risk_level=result_data["risk_level"],
            summary=result_data["summary"],
            possible_causes=result_data["possible_causes"],
            home_care=result_data["home_care"],
            warning_signs=result_data["warning_signs"],
            questions_to_ask=result_data["questions_to_ask"],
            need_vet=result_data["need_vet"],
            disclaimer=result_data["disclaimer"],
            raw_json=result_data,
        )
        conversation.title = conversation.title or message[:40] or "AI 健康咨询"
        conversation.save(update_fields=["title", "updated_at"])

    return ConsultationPayload(
        conversation=conversation,
        user_message=user_record,
        assistant_message=assistant_record,
        result=result,
        reply=reply,
    )


def parse_ai_json(reply_text):
    text = (reply_text or "").strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, flags=re.S | re.I)
    if fenced:
        text = fenced.group(1).strip()
    try:
        parsed = json.loads(text)
    except (TypeError, ValueError):
        return None
    return parsed if isinstance(parsed, dict) else None


def normalize_result(data, raw_text=""):
    if not isinstance(data, dict):
        summary = (raw_text or "AI 返回内容暂时无法结构化，请补充更多症状信息。").strip()
        return {
            "risk_level": "unknown",
            "summary": summary[:200],
            "possible_causes": ["信息不足，需要结合更多症状判断"],
            "home_care": ["先观察精神、食欲、饮水和排便排尿变化", "记录症状出现时间和频率"],
            "need_vet": True,
            "warning_signs": ["如果症状持续或加重，请尽快联系线下宠物医院"],
            "questions_to_ask": ["症状持续多久了？", "精神状态和平时相比如何？", "是否有呕吐、腹泻或误食可能？"],
            "disclaimer": DISCLAIMER,
        }

    risk_level = data.get("risk_level")
    if risk_level not in VALID_RISK_LEVELS:
        risk_level = "unknown"

    possible_causes = normalize_list(data.get("possible_causes"))[:5]
    home_care = normalize_list(data.get("home_care"))[:6]
    warning_signs = normalize_list(data.get("warning_signs"))
    questions_to_ask = normalize_list(data.get("questions_to_ask"))[:3]

    if not possible_causes:
        possible_causes = ["信息不足，需要结合更多症状判断"]
    if len(home_care) < 2:
        home_care = home_care + ["保持清洁饮水并观察精神状态", "记录症状变化和发生频率"]
    if not warning_signs:
        warning_signs = ["如果症状持续或加重，请尽快联系线下宠物医院"]
    if not questions_to_ask:
        questions_to_ask = ["症状持续多久了？", "食欲和饮水是否正常？"]

    need_vet = data.get("need_vet")
    if not isinstance(need_vet, bool):
        need_vet = risk_level in {"medium", "high", "unknown"}
    if risk_level == "high":
        need_vet = True

    summary = str(data.get("summary") or "根据目前信息，建议补充更多症状细节后再做风险判断。")[:500]

    return {
        "risk_level": risk_level,
        "summary": summary,
        "possible_causes": possible_causes,
        "home_care": home_care,
        "need_vet": need_vet,
        "warning_signs": warning_signs[:6],
        "questions_to_ask": questions_to_ask,
        "disclaimer": DISCLAIMER,
    }


def normalize_list(value):
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def user_safe_ai_error(exc):
    if isinstance(exc, AIProviderError):
        return "AI 服务暂时不可用，请稍后重试"
    return "AI 健康咨询暂时不可用，请稍后重试"
