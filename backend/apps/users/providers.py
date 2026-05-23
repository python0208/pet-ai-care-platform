from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class WeChatSession:
    openid: str
    unionid: str = ""


class WeChatProviderBase:
    def code_to_session(self, code: str) -> WeChatSession:
        raise NotImplementedError


class MockWeChatProvider(WeChatProviderBase):
    def code_to_session(self, code: str) -> WeChatSession:
        return WeChatSession(openid=f"mock_{code}")


class WeChatMiniProgramProvider(WeChatProviderBase):
    def code_to_session(self, code: str) -> WeChatSession:
        appid = getattr(settings, "WECHAT_MINI_APPID", "")
        secret = getattr(settings, "WECHAT_MINI_SECRET", "")
        if not appid or not secret:
            raise RuntimeError("微信小程序配置未启用")
        raise NotImplementedError("真实微信 code2session 将在后续阶段接入")


def get_wechat_provider() -> WeChatProviderBase:
    if getattr(settings, "WECHAT_LOGIN_MOCK", True):
        return MockWeChatProvider()
    return WeChatMiniProgramProvider()
