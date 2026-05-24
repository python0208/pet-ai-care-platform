# Generated for Phase 3 AI health consultation.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def seed_prompt_template(apps, schema_editor):
    PromptTemplate = apps.get_model("ai_chat", "PromptTemplate")
    from apps.ai_chat.prompts import PET_HEALTH_CONSULT_PROMPT, PET_HEALTH_CONSULT_SCENE

    PromptTemplate.objects.get_or_create(
        scene=PET_HEALTH_CONSULT_SCENE,
        is_active=True,
        defaults={
            "name": "宠物健康咨询默认提示词",
            "content": PET_HEALTH_CONSULT_PROMPT,
            "version": "v1",
        },
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("pets", "0002_alter_pet_avatar"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AIConversation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("title", models.CharField(max_length=128, verbose_name="会话标题")),
                ("model_provider", models.CharField(blank=True, max_length=64, verbose_name="模型提供方")),
                ("model_name", models.CharField(blank=True, max_length=128, verbose_name="模型名称")),
                ("status", models.CharField(choices=[("active", "活跃"), ("archived", "已归档"), ("deleted", "已删除")], default="active", max_length=32, verbose_name="状态")),
                ("pet", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ai_conversations", to="pets.pet", verbose_name="宠物")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_conversations", to=settings.AUTH_USER_MODEL, verbose_name="用户")),
            ],
            options={
                "verbose_name": "AI 会话",
                "verbose_name_plural": "AI 会话",
                "ordering": ["-updated_at", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PromptTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("name", models.CharField(max_length=128, verbose_name="模板名称")),
                ("scene", models.CharField(max_length=64, verbose_name="场景")),
                ("content", models.TextField(verbose_name="模板内容")),
                ("is_active", models.BooleanField(default=True, verbose_name="启用")),
                ("version", models.CharField(default="v1", max_length=32, verbose_name="版本")),
            ],
            options={
                "verbose_name": "提示词模板",
                "verbose_name_plural": "提示词模板",
                "ordering": ["scene", "-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="AIMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("system", "系统"), ("user", "用户"), ("assistant", "助手")], max_length=20, verbose_name="角色")),
                ("content", models.TextField(verbose_name="内容")),
                ("image_urls", models.JSONField(blank=True, default=list, verbose_name="图片 URL")),
                ("token_count", models.PositiveIntegerField(blank=True, null=True, verbose_name="Token 数")),
                ("raw_response", models.JSONField(blank=True, null=True, verbose_name="模型原始响应")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="ai_chat.aiconversation", verbose_name="会话")),
            ],
            options={
                "verbose_name": "AI 消息",
                "verbose_name_plural": "AI 消息",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="AIConsultationResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("risk_level", models.CharField(choices=[("low", "低风险"), ("medium", "中风险"), ("high", "高风险"), ("unknown", "信息不足")], default="unknown", max_length=20, verbose_name="风险等级")),
                ("summary", models.TextField(blank=True, verbose_name="症状总结")),
                ("possible_causes", models.JSONField(blank=True, default=list, verbose_name="可能原因")),
                ("home_care", models.JSONField(blank=True, default=list, verbose_name="护理建议")),
                ("warning_signs", models.JSONField(blank=True, default=list, verbose_name="危险信号")),
                ("questions_to_ask", models.JSONField(blank=True, default=list, verbose_name="补充问题")),
                ("need_vet", models.BooleanField(default=True, verbose_name="是否建议就医")),
                ("disclaimer", models.TextField(verbose_name="免责声明")),
                ("raw_json", models.JSONField(blank=True, default=dict, verbose_name="结构化原始结果")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="consultation_results", to="ai_chat.aiconversation", verbose_name="会话")),
            ],
            options={
                "verbose_name": "AI 咨询结果",
                "verbose_name_plural": "AI 咨询结果",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="prompttemplate",
            index=models.Index(fields=["scene", "is_active"], name="ai_prompt_scene_active_idx"),
        ),
        migrations.AddIndex(
            model_name="aiconversation",
            index=models.Index(fields=["user", "status"], name="ai_conv_user_status_idx"),
        ),
        migrations.AddIndex(
            model_name="aiconversation",
            index=models.Index(fields=["pet"], name="ai_conv_pet_idx"),
        ),
        migrations.AddIndex(
            model_name="aimessage",
            index=models.Index(fields=["conversation"], name="ai_msg_conv_idx"),
        ),
        migrations.AddIndex(
            model_name="aimessage",
            index=models.Index(fields=["role"], name="ai_msg_role_idx"),
        ),
        migrations.AddIndex(
            model_name="aiconsultationresult",
            index=models.Index(fields=["conversation"], name="ai_result_conv_idx"),
        ),
        migrations.AddIndex(
            model_name="aiconsultationresult",
            index=models.Index(fields=["risk_level"], name="ai_result_risk_idx"),
        ),
        migrations.RunPython(seed_prompt_template, migrations.RunPython.noop),
    ]
