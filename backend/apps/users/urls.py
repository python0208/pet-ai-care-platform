from django.urls import path

from apps.users.views import (
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    TokenRefreshView,
    WeChatLoginView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("auth/wx-login/", WeChatLoginView.as_view(), name="auth-wx-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("users/me/", MeView.as_view(), name="users-me"),
]
