import json

from apps.ai_chat.prompts import DISCLAIMER
from apps.ai_chat.providers.base import AIProviderBase


class MockAIProvider(AIProviderBase):
    provider_name = "mock"

    def __init__(self, model="mock-pet-health"):
        self.model = model

    def chat(self, messages, images=None, stream=False, response_format=None):
        result = {
            "risk_level": "unknown",
            "summary": "目前信息还不够完整，建议先补充症状持续时间、精神状态、食欲饮水和排便排尿情况。",
            "possible_causes": ["饮食变化或短暂肠胃不适", "环境应激", "需要结合更多症状判断"],
            "home_care": ["先观察精神、食欲、饮水和排便排尿变化", "保持清洁饮水，暂时避免突然更换食物", "记录症状出现时间和频率"],
            "need_vet": True,
            "warning_signs": ["如果症状持续或加重，请尽快联系线下宠物医院"],
            "questions_to_ask": ["症状持续多久了？", "是否有呕吐、腹泻或精神明显变差？", "最近是否更换食物或可能误食异物？"],
            "disclaimer": DISCLAIMER,
        }
        return json.dumps(result, ensure_ascii=False)
