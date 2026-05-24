from django.contrib.auth import get_user_model
import hashlib

from rest_framework import permissions, serializers, status
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.common.responses import error_response
from apps.common.responses import success_response
from apps.users.providers import WechatLoginError, get_wechat_provider
from apps.users.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
    build_token_payload,
)

User = get_user_model()


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(build_token_payload(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return success_response(build_token_payload(serializer.validated_data["user"]))


class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc
        return success_response(serializer.validated_data)


class WeChatLoginView(APIView):
    permission_classes = []

    def post(self, request):
        code = request.data.get("code")
        if not code:
            raise serializers.ValidationError({"code": "code 不能为空"})
        platform = request.data.get("platform") or "miniapp"

        try:
            session = get_wechat_provider(platform=platform).code_to_session(code)
        except WechatLoginError as exc:
            return error_response(
                code=40001,
                message=str(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_user = request.user if request.user.is_authenticated else None
        existing_user = User.objects.filter(wx_openid=session.openid).first()
        created = False

        if current_user:
            if existing_user and existing_user.id != current_user.id:
                return error_response(
                    code=40901,
                    message="该微信已绑定其他账号",
                    status=status.HTTP_409_CONFLICT,
                )
            user = current_user
            update_fields = []
            if user.wx_openid != session.openid:
                user.wx_openid = session.openid
                update_fields.append("wx_openid")
            if session.unionid and user.wx_unionid != session.unionid:
                user.wx_unionid = session.unionid
                update_fields.append("wx_unionid")
            update_fields.extend(self._update_profile_from_request(user, request))
            if update_fields:
                user.save(update_fields=sorted(set(update_fields)))
        else:
            if existing_user:
                user = existing_user
                update_fields = self._update_profile_from_request(user, request)
                if session.unionid and user.wx_unionid != session.unionid:
                    user.wx_unionid = session.unionid
                    update_fields.append("wx_unionid")
                if update_fields:
                    user.save(update_fields=sorted(set(update_fields)))
            else:
                user = User.objects.create_user(
                    email=self._build_internal_wechat_email(session.openid),
                    password=None,
                    nickname=request.data.get("nickname") or "微信用户",
                    avatar=request.data.get("avatar") or "",
                    wx_openid=session.openid,
                    wx_unionid=session.unionid,
                )
                created = True

        payload = build_token_payload(user)
        payload["is_new_user"] = created
        return success_response(payload)

    def _update_profile_from_request(self, user, request):
        update_fields = []
        for field in ("nickname", "avatar"):
            value = request.data.get(field)
            if value and getattr(user, field) != value:
                setattr(user, field, value)
                update_fields.append(field)
        return update_fields

    def _build_internal_wechat_email(self, openid):
        digest = hashlib.sha256(openid.encode("utf-8")).hexdigest()[:24]
        return f"wx_{digest}@wechat.local"


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return success_response({})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return success_response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(UserSerializer(request.user).data)


class MeSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.ai_chat.models import AIActionDraft, AIConversation
        from apps.pets.models import Pet

        return success_response(
            {
                "pet_count": Pet.objects.filter(owner=request.user).count(),
                "ai_conversation_count": AIConversation.objects.filter(
                    user=request.user,
                    status__in=[
                        AIConversation.Status.ACTIVE,
                        AIConversation.Status.ARCHIVED,
                    ],
                ).count(),
                "pending_action_count": AIActionDraft.objects.filter(
                    user=request.user,
                    status=AIActionDraft.Status.PENDING,
                ).count(),
                "has_wechat_bound": bool(request.user.wx_openid),
            }
        )
