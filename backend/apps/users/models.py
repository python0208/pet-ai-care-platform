from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.common.models import TimeStampedModel
from apps.users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    class Gender(models.TextChoices):
        UNKNOWN = "unknown", "未知"
        MALE = "male", "男"
        FEMALE = "female", "女"

    email = models.EmailField("邮箱", unique=True)
    nickname = models.CharField("昵称", max_length=64, blank=True)
    avatar = models.URLField("头像", max_length=500, blank=True)
    gender = models.CharField(
        "性别",
        max_length=20,
        choices=Gender.choices,
        default=Gender.UNKNOWN,
    )
    wx_openid = models.CharField(
        "微信 OpenID",
        max_length=128,
        unique=True,
        null=True,
        blank=True,
    )
    wx_unionid = models.CharField("微信 UnionID", max_length=128, blank=True)
    app_openid = models.CharField("App OpenID", max_length=128, blank=True)
    is_email_verified = models.BooleanField("邮箱已验证", default=False)
    is_active = models.BooleanField("启用", default=True)
    is_staff = models.BooleanField("员工", default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        indexes = [
            models.Index(fields=["email"], name="users_user_email_243f6e_idx"),
            models.Index(fields=["wx_openid"], name="users_user_wx_open_f7a52e_idx"),
        ]

    def __str__(self):
        return self.email
