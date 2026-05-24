from apps.ai_chat.providers.base import (
    AIConfigurationError,
    AIProviderBase,
    AIProviderError,
)


class OpenAICompatibleProvider(AIProviderBase):
    provider_name = "openai_compatible"

    def __init__(
        self,
        api_base,
        api_key,
        model,
        timeout=60,
        temperature=0.3,
        max_tokens=1200,
        provider_name=None,
    ):
        if not api_base:
            raise AIConfigurationError("AI_API_BASE 未配置")
        if not api_key:
            raise AIConfigurationError("AI_API_KEY 未配置")
        if not model:
            raise AIConfigurationError("AI_MODEL 未配置")
        self.api_base = api_base
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        if provider_name:
            self.provider_name = provider_name

    def chat(self, messages, images=None, stream=False, response_format=None):
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                timeout=self.timeout,
            )
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": stream,
            }
            if response_format:
                kwargs["response_format"] = response_format
            try:
                response = client.chat.completions.create(**kwargs)
            except Exception as exc:
                if response_format and "response_format" in str(exc):
                    kwargs.pop("response_format", None)
                    response = client.chat.completions.create(**kwargs)
                else:
                    raise
            return response.choices[0].message.content or ""
        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError("AI 服务暂时不可用，请稍后重试") from exc
