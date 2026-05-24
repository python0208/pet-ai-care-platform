from abc import ABC, abstractmethod


class AIProviderError(Exception):
    """Base exception for user-safe AI provider failures."""


class AIConfigurationError(AIProviderError):
    """Raised when AI provider settings are incomplete."""


class AIProviderBase(ABC):
    provider_name = "base"

    @abstractmethod
    def chat(self, messages, images=None, stream=False, response_format=None):
        raise NotImplementedError
