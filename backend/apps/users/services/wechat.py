import json
import urllib.parse
import urllib.request
from dataclasses import dataclass

from django.conf import settings


class WechatLoginError(Exception):
    """Base exception for user-facing WeChat login failures."""


class WechatConfigError(WechatLoginError):
    pass


class WechatProviderError(WechatLoginError):
    pass


@dataclass(frozen=True)
class WechatSession:
    openid: str
    unionid: str = ""
    session_key: str = ""


class WechatLoginProviderBase:
    platform = ""

    def code_to_session(self, code: str) -> WechatSession:
        raise NotImplementedError


class MockWechatProvider(WechatLoginProviderBase):
    platform = "mock"

    def code_to_session(self, code: str) -> WechatSession:
        clean_code = (code or "").strip()
        if not clean_code:
            raise WechatProviderError("微信登录 code 不能为空")
        return WechatSession(openid=f"mock_{clean_code}", unionid=f"mock_union_{clean_code}")


class WechatMiniProgramProvider(WechatLoginProviderBase):
    platform = "miniapp"
    CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"

    def __init__(self, appid: str, secret: str, timeout: int = 8):
        self.appid = appid
        self.secret = secret
        self.timeout = timeout

    def code_to_session(self, code: str) -> WechatSession:
        if not self.appid or not self.secret:
            raise WechatConfigError("微信小程序登录未配置")
        params = urllib.parse.urlencode(
            {
                "appid": self.appid,
                "secret": self.secret,
                "js_code": code,
                "grant_type": "authorization_code",
            }
        )
        url = f"{self.CODE2SESSION_URL}?{params}"
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise WechatProviderError("微信登录服务暂时不可用，请稍后重试") from exc

        if payload.get("errcode"):
            raise WechatProviderError("微信登录失败，请重新授权后再试")
        openid = payload.get("openid")
        if not openid:
            raise WechatProviderError("微信登录失败，未获取到用户标识")
        return WechatSession(
            openid=openid,
            unionid=payload.get("unionid", ""),
            session_key=payload.get("session_key", ""),
        )


class WechatAppProvider(WechatLoginProviderBase):
    platform = "app"

    def code_to_session(self, code: str) -> WechatSession:
        raise WechatConfigError("App 微信登录暂未配置")


def get_wechat_provider(platform: str = "miniapp") -> WechatLoginProviderBase:
    if not getattr(settings, "WECHAT_LOGIN_ENABLED", True):
        raise WechatConfigError("微信登录暂未启用")

    platform = (platform or "miniapp").lower()
    if platform == "miniapp":
        appid = getattr(settings, "WECHAT_MINI_APPID", "")
        secret = getattr(settings, "WECHAT_MINI_SECRET", "")
        if appid and secret:
            return WechatMiniProgramProvider(appid=appid, secret=secret)
        if getattr(settings, "DEBUG", False) and getattr(
            settings,
            "WECHAT_LOGIN_MOCK_ENABLED",
            False,
        ):
            return MockWechatProvider()
        raise WechatConfigError("微信小程序登录未配置")

    if platform == "app":
        raise WechatConfigError("App 微信登录暂未配置")

    raise WechatConfigError("不支持的微信登录平台")
