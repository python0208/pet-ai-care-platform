from django.conf import settings

from apps.ai_chat.providers.base import AIConfigurationError
from apps.ai_chat.providers.mock_provider import MockAIProvider
from apps.ai_chat.providers.openai_compatible import OpenAICompatibleProvider


class ProviderFactory:
    @staticmethod
    def create():
        provider = settings.AI_PROVIDER
        api_key = settings.AI_API_KEY

        if provider == "mock":
            return MockAIProvider(model=settings.AI_MODEL)

        if provider in {"ark_openai_compatible", "openai_compatible"}:
            if not api_key and settings.DEBUG:
                return MockAIProvider(model=settings.AI_MODEL)
            if not api_key:
                raise AIConfigurationError("AI_API_KEY 未配置")
            return OpenAICompatibleProvider(
                api_base=settings.AI_API_BASE,
                api_key=api_key,
                model=settings.AI_MODEL,
                timeout=settings.AI_TIMEOUT_SECONDS,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                provider_name=provider,
            )

        raise AIConfigurationError("AI_PROVIDER 配置不支持")
