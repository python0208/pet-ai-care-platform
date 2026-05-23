from django.contrib.auth import get_user_model
from rest_framework import permissions, serializers, status
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.common.responses import success_response
from apps.users.providers import get_wechat_provider
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
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        code = request.data.get("code")
        if not code:
            raise serializers.ValidationError({"code": "code 不能为空"})

        session = get_wechat_provider().code_to_session(code)
        user, created = User.objects.get_or_create(
            wx_openid=session.openid,
            defaults={
                "email": f"{session.openid}@wechat.local",
                "nickname": request.data.get("nickname") or "微信用户",
                "avatar": request.data.get("avatar") or "",
                "wx_unionid": session.unionid,
            },
        )
        if not created:
            update_fields = []
            for field in ("nickname", "avatar"):
                value = request.data.get(field)
                if value:
                    setattr(user, field, value)
                    update_fields.append(field)
            if session.unionid and user.wx_unionid != session.unionid:
                user.wx_unionid = session.unionid
                update_fields.append("wx_unionid")
            if update_fields:
                user.save(update_fields=update_fields)

        return success_response(build_token_payload(user))


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
