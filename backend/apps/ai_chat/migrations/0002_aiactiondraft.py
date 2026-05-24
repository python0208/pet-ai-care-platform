import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def refresh_default_prompt(apps, schema_editor):
    PromptTemplate = apps.get_model("ai_chat", "PromptTemplate")
    from apps.ai_chat.prompts import PET_HEALTH_CONSULT_PROMPT, PET_HEALTH_CONSULT_SCENE

    PromptTemplate.objects.filter(scene=PET_HEALTH_CONSULT_SCENE, is_active=True).update(
        name="宠物养护助手默认提示词",
        content=PET_HEALTH_CONSULT_PROMPT,
        version="v2",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("ai_chat", "0001_initial"),
        ("pets", "0002_alter_pet_avatar"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AIActionDraft",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("action_type", models.CharField(choices=[("create_weight_record", "创建体重记录"), ("create_health_record", "创建健康记录")], max_length=64, verbose_name="动作类型")),
                ("display_title", models.CharField(max_length=128, verbose_name="展示标题")),
                ("confirm_text", models.CharField(max_length=255, verbose_name="确认文案")),
                ("payload", models.JSONField(blank=True, default=dict, verbose_name="动作载荷")),
                ("status", models.CharField(choices=[("pending", "待确认"), ("confirmed", "已确认"), ("cancelled", "已取消"), ("executed", "已执行"), ("failed", "执行失败")], default="pending", max_length=32, verbose_name="状态")),
                ("result_ref_type", models.CharField(blank=True, max_length=64, verbose_name="结果资源类型")),
                ("result_ref_id", models.PositiveBigIntegerField(blank=True, null=True, verbose_name="结果资源 ID")),
                ("error_message", models.CharField(blank=True, max_length=255, verbose_name="失败原因")),
                ("executed_at", models.DateTimeField(blank=True, null=True, verbose_name="执行时间")),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="action_drafts", to="ai_chat.aiconversation", verbose_name="会话")),
                ("pet", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_action_drafts", to="pets.pet", verbose_name="宠物")),
                ("source_message", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="action_drafts", to="ai_chat.aimessage", verbose_name="来源消息")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_action_drafts", to=settings.AUTH_USER_MODEL, verbose_name="用户")),
            ],
            options={
                "verbose_name": "AI 动作草稿",
                "verbose_name_plural": "AI 动作草稿",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="aiactiondraft",
            index=models.Index(fields=["user", "status"], name="ai_draft_user_status_idx"),
        ),
        migrations.AddIndex(
            model_name="aiactiondraft",
            index=models.Index(fields=["conversation"], name="ai_draft_conv_idx"),
        ),
        migrations.AddIndex(
            model_name="aiactiondraft",
            index=models.Index(fields=["pet"], name="ai_draft_pet_idx"),
        ),
        migrations.RunPython(refresh_default_prompt, migrations.RunPython.noop),
    ]
