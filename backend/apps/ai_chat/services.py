import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.ai_chat.models import (
    AIActionDraft,
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
from apps.pets.models import HealthRecord, Pet, WeightRecord
from apps.pets.serializers import HealthRecordSerializer, WeightRecordSerializer

VALID_MODES = {"daily_care", "health_consultation", "record_intent", "mixed", "unknown"}
VALID_RISK_LEVELS = {"low", "medium", "high", "unknown"}
SUPPORTED_ACTION_TYPES = {
    AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
    AIActionDraft.ActionType.CREATE_HEALTH_RECORD,
}
HEALTH_RECORD_TYPE_ALIASES = {
    "vaccine": HealthRecord.RecordType.VACCINE,
    "vaccination": HealthRecord.RecordType.VACCINE,
    "疫苗": HealthRecord.RecordType.VACCINE,
    "接种": HealthRecord.RecordType.VACCINE,
    "免疫": HealthRecord.RecordType.VACCINE,
    "deworm": HealthRecord.RecordType.DEWORM,
    "deworming": HealthRecord.RecordType.DEWORM,
    "驱虫": HealthRecord.RecordType.DEWORM,
    "体内驱虫": HealthRecord.RecordType.DEWORM,
    "体外驱虫": HealthRecord.RecordType.DEWORM,
    "体内外驱虫": HealthRecord.RecordType.DEWORM,
    "medical": HealthRecord.RecordType.MEDICAL,
    "visit": HealthRecord.RecordType.MEDICAL,
    "就诊": HealthRecord.RecordType.MEDICAL,
    "就医": HealthRecord.RecordType.MEDICAL,
    "检查": HealthRecord.RecordType.MEDICAL,
    "allergy": HealthRecord.RecordType.ALLERGY,
    "过敏": HealthRecord.RecordType.ALLERGY,
    "过敏史": HealthRecord.RecordType.ALLERGY,
    "other": HealthRecord.RecordType.OTHER,
    "其他": HealthRecord.RecordType.OTHER,
}
HEALTH_RECORD_TYPE_TITLES = {
    HealthRecord.RecordType.VACCINE: "疫苗记录",
    HealthRecord.RecordType.DEWORM: "驱虫记录",
    HealthRecord.RecordType.MEDICAL: "就诊记录",
    HealthRecord.RecordType.ALLERGY: "过敏记录",
    HealthRecord.RecordType.OTHER: "健康记录",
}


@dataclass
class ConsultationPayload:
    conversation: AIConversation
    user_message: AIMessage
    assistant_message: AIMessage
    result: AIConsultationResult
    reply: str
    mode: str
    health_result: dict | None
    action_drafts: list[AIActionDraft]
    questions_to_ask: list[str]
    disclaimer: str


def get_owned_conversation(user, conversation_id):
    return get_object_or_404(
        AIConversation.objects.select_related("pet", "user"),
        id=conversation_id,
        user=user,
        status__in=[AIConversation.Status.ACTIVE, AIConversation.Status.ARCHIVED],
    )


def get_owned_pet(user, pet_id):
    return get_object_or_404(Pet, id=pet_id, owner=user)


def get_owned_action_draft(user, draft_id):
    return get_object_or_404(
        AIActionDraft.objects.select_related("pet", "conversation"),
        id=draft_id,
        user=user,
    )


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
        f"宠物 ID：{pet.id}",
        f"宠物名称：{pet.name}",
        f"物种：{pet.get_species_display()}",
        f"品种：{pet.breed or '未填写'}",
        f"性别：{pet.get_gender_display()}",
        f"年龄：{format_age(pet.birthday, today)}",
        f"体重：{pet.weight}kg" if pet.weight is not None else "体重：未填写",
        f"是否绝育：{'是' if pet.neutered else '否'}",
        f"备注：{pet.remark or '无'}",
        f"今天日期：{today.isoformat()}",
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
            "用户当前消息：",
            user_message or "用户上传了图片，请结合图片信息和宠物档案给出建议。",
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
                title=(message or "图片咨询")[:40] or "AI 养宠助手",
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
            content=message or "请参考我上传的图片",
            image_urls=image_urls,
        )

    messages = build_messages(pet, message, image_urls)
    reply_text = provider.chat(
        messages=messages,
        images=image_urls,
        response_format={"type": "json_object"},
    )
    normalized = normalize_ai_payload(parse_ai_json(reply_text), reply_text, pet, message)
    health_result = normalized["health_result"]
    result_data = health_result or empty_health_result()

    with transaction.atomic():
        assistant_record = AIMessage.objects.create(
            conversation=conversation,
            role=AIMessage.Role.ASSISTANT,
            content=normalized["reply"],
            image_urls=[],
            raw_response={
                "raw_text": reply_text,
                "parsed_result": normalized,
            },
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
        action_drafts = create_action_drafts_from_payload(
            user=user,
            pet=pet,
            conversation=conversation,
            source_message=assistant_record,
            drafts=normalized["action_drafts"],
        )
        if not conversation.title:
            conversation.title = (message or normalized["reply"])[:40] or "AI 养宠助手"
        conversation.save(update_fields=["title", "updated_at"])

    return ConsultationPayload(
        conversation=conversation,
        user_message=user_record,
        assistant_message=assistant_record,
        result=result,
        reply=normalized["reply"],
        mode=normalized["mode"],
        health_result=health_result,
        action_drafts=action_drafts,
        questions_to_ask=normalized["questions_to_ask"],
        disclaimer=normalized["disclaimer"],
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


def normalize_ai_payload(data, raw_text="", pet=None, user_message=""):
    if not isinstance(data, dict):
        fallback = empty_health_result(
            summary=(raw_text or "AI 返回内容暂时无法结构化，请补充更多信息。").strip()[:200],
            need_vet=True,
        )
        return {
            "mode": "unknown",
            "reply": fallback["summary"],
            "health_result": fallback,
            "action_drafts": [],
            "questions_to_ask": fallback["questions_to_ask"],
            "disclaimer": "如涉及健康问题，本结果仅供养宠护理参考，不能替代专业兽医诊断。",
        }

    mode = data.get("mode")
    if mode not in VALID_MODES:
        mode = "unknown"

    health_result = None
    if isinstance(data.get("health_result"), dict):
        health_result = normalize_health_result(data["health_result"])
    elif mode == "health_consultation":
        health_result = empty_health_result(need_vet=True)

    reply = str(data.get("reply") or "").strip()
    if not reply:
        reply = health_result["summary"] if health_result else "我可以帮你整理养宠建议，也可以把明确的档案内容生成待确认记录。"

    action_drafts = normalize_action_drafts(data.get("action_drafts"), pet, user_message)
    if not action_drafts:
        action_drafts = infer_action_drafts_from_message(user_message, pet)
    questions_to_ask = normalize_list(data.get("questions_to_ask"))[:5]

    return {
        "mode": mode,
        "reply": reply[:1200],
        "health_result": health_result,
        "action_drafts": action_drafts,
        "questions_to_ask": questions_to_ask,
        "disclaimer": "如涉及健康问题，本结果仅供养宠护理参考，不能替代专业兽医诊断。",
    }


def normalize_health_result(data):
    risk_level = data.get("risk_level")
    if risk_level not in VALID_RISK_LEVELS:
        risk_level = "unknown"

    possible_causes = normalize_list(data.get("possible_causes"))[:5]
    home_care = normalize_list(data.get("home_care"))[:6]
    warning_signs = normalize_list(data.get("warning_signs"))[:6]
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

    return {
        "risk_level": risk_level,
        "summary": str(data.get("summary") or "根据目前信息，建议补充更多细节后再做风险判断。")[:500],
        "possible_causes": possible_causes,
        "home_care": home_care,
        "need_vet": need_vet,
        "warning_signs": warning_signs,
        "questions_to_ask": questions_to_ask,
        "disclaimer": DISCLAIMER,
    }


def empty_health_result(summary="", need_vet=False):
    return {
        "risk_level": "unknown",
        "summary": summary,
        "possible_causes": [],
        "home_care": [],
        "need_vet": need_vet,
        "warning_signs": [],
        "questions_to_ask": [],
        "disclaimer": DISCLAIMER if summary or need_vet else "",
    }


def normalize_action_drafts(value, pet, user_message=""):
    if not isinstance(value, list) or pet is None:
        return []
    drafts = []
    for item in value[:3]:
        if not isinstance(item, dict):
            continue
        action_type = item.get("action_type")
        if action_type not in SUPPORTED_ACTION_TYPES:
            continue
        payload = item.get("payload")
        if not isinstance(payload, dict):
            continue
        payload = normalize_action_payload(action_type, payload, pet, user_message)
        if not validate_action_payload(action_type, payload):
            continue
        drafts.append(
            {
                "action_type": action_type,
                "display_title": str(item.get("display_title") or default_draft_title(action_type))[:128],
                "confirm_text": str(item.get("confirm_text") or default_confirm_text(action_type, pet, payload))[:255],
                "payload": payload,
                "need_confirm": True,
            }
        )
    return drafts


def normalize_action_payload(action_type, payload, pet, user_message=""):
    payload = dict(payload)
    payload["pet_id"] = pet.id
    payload["record_date"] = normalize_record_date(payload.get("record_date"))
    if action_type == AIActionDraft.ActionType.CREATE_HEALTH_RECORD:
        record_type = normalize_health_record_type(payload.get("record_type"), user_message)
        payload["record_type"] = record_type
        payload["title"] = str(payload.get("title") or default_health_record_title(record_type, user_message))[:128]
        payload["description"] = str(
            payload.get("description") or f"用户通过 AI 对话记录：{user_message}"
        )
        attachments = payload.get("attachments")
        payload["attachments"] = attachments if isinstance(attachments, list) else []
    return payload


def normalize_record_date(value):
    if not value:
        return timezone.localdate().isoformat()
    return str(value)[:10]


def normalize_health_record_type(value, user_message=""):
    key = str(value or "").strip().lower()
    if key in HEALTH_RECORD_TYPE_ALIASES:
        return HEALTH_RECORD_TYPE_ALIASES[key]
    message = user_message or ""
    if "疫苗" in message or "接种" in message or "免疫" in message:
        return HealthRecord.RecordType.VACCINE
    if "驱虫" in message:
        return HealthRecord.RecordType.DEWORM
    if "过敏" in message:
        return HealthRecord.RecordType.ALLERGY
    if any(word in message for word in ["就诊", "就医", "医院", "检查", "复诊"]):
        return HealthRecord.RecordType.MEDICAL
    return HealthRecord.RecordType.OTHER


def default_health_record_title(record_type, user_message=""):
    base_title = HEALTH_RECORD_TYPE_TITLES.get(record_type, "健康记录")
    if record_type == HealthRecord.RecordType.ALLERGY:
        match = re.search(r"对(.{1,20}?)(?:过敏|敏感)", user_message or "")
        if match:
            return f"对{match.group(1).strip()}过敏"
    return base_title


def infer_action_drafts_from_message(user_message, pet):
    if pet is None:
        return []
    message = (user_message or "").strip()
    if not message:
        return []

    weight_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|公斤|千克)", message, flags=re.I)
    if weight_match and ("体重" in message or "称重" in message or "记录" in message):
        payload = {
            "pet_id": pet.id,
            "record_type": "weight",
            "weight": weight_match.group(1),
            "record_date": timezone.localdate().isoformat(),
            "remark": "用户通过 AI 对话记录",
        }
        return [
            {
                "action_type": AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
                "display_title": "建议添加体重记录",
                "confirm_text": default_confirm_text(
                    AIActionDraft.ActionType.CREATE_WEIGHT_RECORD,
                    pet,
                    payload,
                ),
                "payload": payload,
                "need_confirm": True,
            }
        ]

    if not any(word in message for word in ["记录", "接种", "疫苗", "驱虫", "过敏", "就诊", "就医", "医院", "检查"]):
        return []

    record_type = normalize_health_record_type("", message)
    if record_type == HealthRecord.RecordType.OTHER:
        return []
    payload = {
        "pet_id": pet.id,
        "record_type": record_type,
        "title": default_health_record_title(record_type, message),
        "record_date": timezone.localdate().isoformat(),
        "description": f"用户通过 AI 对话记录：{message}",
        "attachments": [],
    }
    return [
        {
            "action_type": AIActionDraft.ActionType.CREATE_HEALTH_RECORD,
            "display_title": f"建议添加{HEALTH_RECORD_TYPE_TITLES.get(record_type, '健康记录')}",
            "confirm_text": default_confirm_text(
                AIActionDraft.ActionType.CREATE_HEALTH_RECORD,
                pet,
                payload,
            ),
            "payload": payload,
            "need_confirm": True,
        }
    ]


def validate_action_payload(action_type, payload):
    if action_type == AIActionDraft.ActionType.CREATE_WEIGHT_RECORD:
        try:
            Decimal(str(payload.get("weight")))
        except (InvalidOperation, TypeError, ValueError):
            return False
        return bool(payload.get("record_date"))

    if action_type == AIActionDraft.ActionType.CREATE_HEALTH_RECORD:
        return (
            payload.get("record_type") in HealthRecord.RecordType.values
            and bool(payload.get("title"))
            and bool(payload.get("record_date"))
        )
    return False


def create_action_drafts_from_payload(user, pet, conversation, source_message, drafts):
    created = []
    for draft in drafts:
        created.append(
            AIActionDraft.objects.create(
                user=user,
                pet=pet,
                conversation=conversation,
                source_message=source_message,
                action_type=draft["action_type"],
                display_title=draft["display_title"],
                confirm_text=draft["confirm_text"],
                payload=draft["payload"],
            )
        )
    return created


def confirm_action_draft(user, draft):
    if draft.user_id != user.id:
        raise PermissionError("无权限")
    if draft.status == AIActionDraft.Status.EXECUTED:
        raise ValueError("该记录草稿已保存")
    if draft.status == AIActionDraft.Status.CANCELLED:
        raise ValueError("该记录草稿已取消")
    if draft.pet.owner_id != user.id:
        raise PermissionError("无权限")

    try:
        with transaction.atomic():
            if draft.action_type == AIActionDraft.ActionType.CREATE_WEIGHT_RECORD:
                result = execute_weight_record(draft)
                ref_type = "weight_record"
            elif draft.action_type == AIActionDraft.ActionType.CREATE_HEALTH_RECORD:
                result = execute_health_record(draft)
                ref_type = "health_record"
            else:
                raise ValueError("不支持的动作类型")

            draft.status = AIActionDraft.Status.EXECUTED
            draft.result_ref_type = ref_type
            draft.result_ref_id = result.id
            draft.error_message = ""
            draft.executed_at = timezone.now()
            draft.save(
                update_fields=[
                    "status",
                    "result_ref_type",
                    "result_ref_id",
                    "error_message",
                    "executed_at",
                    "updated_at",
                ]
            )
            return draft
    except Exception as exc:
        draft.status = AIActionDraft.Status.FAILED
        draft.error_message = str(exc)[:255]
        draft.save(update_fields=["status", "error_message", "updated_at"])
        raise


def execute_weight_record(draft):
    payload = draft.payload
    pet = get_owned_pet(draft.user, payload.get("pet_id"))
    serializer = WeightRecordSerializer(
        data={
            "weight": payload.get("weight"),
            "record_date": payload.get("record_date"),
            "remark": payload.get("remark") or "用户通过 AI 对话记录",
        }
    )
    serializer.is_valid(raise_exception=True)
    record = serializer.save(pet=pet)
    pet.weight = record.weight
    pet.save(update_fields=["weight", "updated_at"])
    return record


def execute_health_record(draft):
    payload = draft.payload
    pet = get_owned_pet(draft.user, payload.get("pet_id"))
    serializer = HealthRecordSerializer(
        data={
            "record_type": payload.get("record_type"),
            "title": payload.get("title"),
            "record_date": payload.get("record_date"),
            "next_remind_date": payload.get("next_remind_date"),
            "hospital": payload.get("hospital") or "",
            "doctor": payload.get("doctor") or "",
            "cost": payload.get("cost"),
            "description": payload.get("description") or "",
            "attachments": payload.get("attachments") or [],
        }
    )
    serializer.is_valid(raise_exception=True)
    return serializer.save(pet=pet)


def cancel_action_draft(user, draft):
    if draft.user_id != user.id:
        raise PermissionError("无权限")
    if draft.status == AIActionDraft.Status.EXECUTED:
        raise ValueError("已保存的记录不能取消")
    draft.status = AIActionDraft.Status.CANCELLED
    draft.save(update_fields=["status", "updated_at"])
    return draft


def default_draft_title(action_type):
    return "建议添加体重记录" if action_type == AIActionDraft.ActionType.CREATE_WEIGHT_RECORD else "建议添加健康记录"


def default_confirm_text(action_type, pet, payload):
    if action_type == AIActionDraft.ActionType.CREATE_WEIGHT_RECORD:
        return f"是否将 {pet.name} {payload.get('record_date')} 的体重 {payload.get('weight')}kg 添加到体重记录？"
    return f"是否将 {pet.name} 的“{payload.get('title', '健康记录')}”添加到健康档案？"


def normalize_list(value):
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def user_safe_ai_error(exc):
    if isinstance(exc, AIProviderError):
        return "AI 服务暂时不可用，请稍后重试"
    return "AI 养宠助手暂时不可用，请稍后重试"
