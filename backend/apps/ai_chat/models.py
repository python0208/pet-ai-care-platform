from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.pets.models import Pet


class AIConversation(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "活跃"
        ARCHIVED = "archived", "已归档"
        DELETED = "deleted", "已删除"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="用户",
        related_name="ai_conversations",
        on_delete=models.CASCADE,
    )
    pet = models.ForeignKey(
        Pet,
        verbose_name="宠物",
        related_name="ai_conversations",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField("会话标题", max_length=128)
    model_provider = models.CharField("模型提供方", max_length=64, blank=True)
    model_name = models.CharField("模型名称", max_length=128, blank=True)
    status = models.CharField(
        "状态",
        max_length=32,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        verbose_name = "AI 会话"
        verbose_name_plural = "AI 会话"
        ordering = ["-updated_at", "-created_at"]
        indexes = [
            models.Index(fields=["user", "status"], name="ai_conv_user_status_idx"),
            models.Index(fields=["pet"], name="ai_conv_pet_idx"),
        ]

    def __str__(self):
        return f"{self.user_id}-{self.title}"


class AIMessage(models.Model):
    class Role(models.TextChoices):
        SYSTEM = "system", "系统"
        USER = "user", "用户"
        ASSISTANT = "assistant", "助手"

    conversation = models.ForeignKey(
        AIConversation,
        verbose_name="会话",
        related_name="messages",
        on_delete=models.CASCADE,
    )
    role = models.CharField("角色", max_length=20, choices=Role.choices)
    content = models.TextField("内容")
    image_urls = models.JSONField("图片 URL", default=list, blank=True)
    token_count = models.PositiveIntegerField("Token 数", null=True, blank=True)
    raw_response = models.JSONField("模型原始响应", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "AI 消息"
        verbose_name_plural = "AI 消息"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation"], name="ai_msg_conv_idx"),
            models.Index(fields=["role"], name="ai_msg_role_idx"),
        ]

    def __str__(self):
        return f"{self.conversation_id}-{self.role}"


class AIConsultationResult(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = "low", "低风险"
        MEDIUM = "medium", "中风险"
        HIGH = "high", "高风险"
        UNKNOWN = "unknown", "信息不足"

    conversation = models.ForeignKey(
        AIConversation,
        verbose_name="会话",
        related_name="consultation_results",
        on_delete=models.CASCADE,
    )
    risk_level = models.CharField(
        "风险等级",
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.UNKNOWN,
    )
    summary = models.TextField("症状总结", blank=True)
    possible_causes = models.JSONField("可能原因", default=list, blank=True)
    home_care = models.JSONField("护理建议", default=list, blank=True)
    warning_signs = models.JSONField("危险信号", default=list, blank=True)
    questions_to_ask = models.JSONField("补充问题", default=list, blank=True)
    need_vet = models.BooleanField("是否建议就医", default=True)
    disclaimer = models.TextField("免责声明")
    raw_json = models.JSONField("结构化原始结果", default=dict, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "AI 咨询结果"
        verbose_name_plural = "AI 咨询结果"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["conversation"], name="ai_result_conv_idx"),
            models.Index(fields=["risk_level"], name="ai_result_risk_idx"),
        ]

    def __str__(self):
        return f"{self.conversation_id}-{self.risk_level}"


class AIActionDraft(TimeStampedModel):
    class ActionType(models.TextChoices):
        CREATE_WEIGHT_RECORD = "create_weight_record", "创建体重记录"
        CREATE_HEALTH_RECORD = "create_health_record", "创建健康记录"

    class Status(models.TextChoices):
        PENDING = "pending", "待确认"
        CONFIRMED = "confirmed", "已确认"
        CANCELLED = "cancelled", "已取消"
        EXECUTED = "executed", "已执行"
        FAILED = "failed", "执行失败"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="用户",
        related_name="ai_action_drafts",
        on_delete=models.CASCADE,
    )
    pet = models.ForeignKey(
        Pet,
        verbose_name="宠物",
        related_name="ai_action_drafts",
        on_delete=models.CASCADE,
    )
    conversation = models.ForeignKey(
        AIConversation,
        verbose_name="会话",
        related_name="action_drafts",
        on_delete=models.CASCADE,
    )
    source_message = models.ForeignKey(
        AIMessage,
        verbose_name="来源消息",
        related_name="action_drafts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action_type = models.CharField("动作类型", max_length=64, choices=ActionType.choices)
    display_title = models.CharField("展示标题", max_length=128)
    confirm_text = models.CharField("确认文案", max_length=255)
    payload = models.JSONField("动作载荷", default=dict, blank=True)
    status = models.CharField(
        "状态",
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    result_ref_type = models.CharField("结果资源类型", max_length=64, blank=True)
    result_ref_id = models.PositiveBigIntegerField("结果资源 ID", null=True, blank=True)
    error_message = models.CharField("失败原因", max_length=255, blank=True)
    executed_at = models.DateTimeField("执行时间", null=True, blank=True)

    class Meta:
        verbose_name = "AI 动作草稿"
        verbose_name_plural = "AI 动作草稿"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"], name="ai_draft_user_status_idx"),
            models.Index(fields=["conversation"], name="ai_draft_conv_idx"),
            models.Index(fields=["pet"], name="ai_draft_pet_idx"),
        ]

    def __str__(self):
        return f"{self.user_id}-{self.action_type}-{self.status}"


class PromptTemplate(TimeStampedModel):
    name = models.CharField("模板名称", max_length=128)
    scene = models.CharField("场景", max_length=64)
    content = models.TextField("模板内容")
    is_active = models.BooleanField("启用", default=True)
    version = models.CharField("版本", max_length=32, default="v1")

    class Meta:
        verbose_name = "提示词模板"
        verbose_name_plural = "提示词模板"
        ordering = ["scene", "-updated_at"]
        indexes = [
            models.Index(fields=["scene", "is_active"], name="ai_prompt_scene_active_idx"),
        ]

    def __str__(self):
        return f"{self.scene}-{self.version}"
