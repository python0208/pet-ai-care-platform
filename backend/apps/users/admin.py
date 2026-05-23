from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-id",)
    list_display = ("id", "email", "nickname", "is_email_verified", "is_active", "is_staff")
    search_fields = ("email", "nickname", "wx_openid")
    list_filter = ("is_active", "is_staff", "is_email_verified", "gender")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("个人资料", {"fields": ("nickname", "avatar", "gender")}),
        ("微信信息", {"fields": ("wx_openid", "wx_unionid", "app_openid")}),
        ("状态", {"fields": ("is_email_verified", "is_active", "is_staff", "is_superuser")}),
        ("权限", {"fields": ("groups", "user_permissions")}),
        ("重要时间", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")
