import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import apps.users.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="邮箱")),
                ("nickname", models.CharField(blank=True, max_length=64, verbose_name="昵称")),
                ("avatar", models.URLField(blank=True, max_length=500, verbose_name="头像")),
                ("gender", models.CharField(choices=[("unknown", "未知"), ("male", "男"), ("female", "女")], default="unknown", max_length=20, verbose_name="性别")),
                ("wx_openid", models.CharField(blank=True, max_length=128, null=True, unique=True, verbose_name="微信 OpenID")),
                ("wx_unionid", models.CharField(blank=True, max_length=128, verbose_name="微信 UnionID")),
                ("app_openid", models.CharField(blank=True, max_length=128, verbose_name="App OpenID")),
                ("is_email_verified", models.BooleanField(default=False, verbose_name="邮箱已验证")),
                ("is_active", models.BooleanField(default=True, verbose_name="启用")),
                ("is_staff", models.BooleanField(default=False, verbose_name="员工")),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={
                "verbose_name": "用户",
                "verbose_name_plural": "用户",
                "indexes": [
                    models.Index(fields=["email"], name="users_user_email_243f6e_idx"),
                    models.Index(fields=["wx_openid"], name="users_user_wx_open_f7a52e_idx"),
                ],
            },
            managers=[
                ("objects", apps.users.managers.UserManager()),
            ],
        ),
    ]
