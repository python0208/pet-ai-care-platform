from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Pet(TimeStampedModel):
    class Species(models.TextChoices):
        CAT = "cat", "猫"
        DOG = "dog", "狗"
        OTHER = "other", "其他"

    class Gender(models.TextChoices):
        MALE = "male", "公"
        FEMALE = "female", "母"
        UNKNOWN = "unknown", "未知"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="所属用户",
        related_name="pets",
        on_delete=models.CASCADE,
    )
    name = models.CharField("宠物名称", max_length=64)
    species = models.CharField(
        "物种",
        max_length=20,
        choices=Species.choices,
        default=Species.CAT,
    )
    breed = models.CharField("品种", max_length=64, blank=True)
    gender = models.CharField(
        "性别",
        max_length=20,
        choices=Gender.choices,
        default=Gender.UNKNOWN,
    )
    birthday = models.DateField("生日", null=True, blank=True)
    avatar = models.URLField("宠物头像", max_length=500, blank=True)
    color = models.CharField("毛色", max_length=64, blank=True)
    weight = models.DecimalField(
        "当前体重",
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    neutered = models.BooleanField("是否绝育", default=False)
    remark = models.TextField("备注", blank=True)

    class Meta:
        verbose_name = "宠物"
        verbose_name_plural = "宠物"
        ordering = ["-updated_at", "-created_at"]
        indexes = [
            models.Index(fields=["owner"], name="pets_pet_owner_idx"),
            models.Index(fields=["species"], name="pets_pet_species_idx"),
        ]

    def __str__(self):
        return f"{self.name}({self.owner_id})"


class HealthRecord(TimeStampedModel):
    class RecordType(models.TextChoices):
        VACCINE = "vaccine", "疫苗"
        DEWORM = "deworm", "驱虫"
        MEDICAL = "medical", "就诊"
        ALLERGY = "allergy", "过敏"
        OTHER = "other", "其他"

    pet = models.ForeignKey(
        Pet,
        verbose_name="宠物",
        related_name="health_records",
        on_delete=models.CASCADE,
    )
    record_type = models.CharField(
        "记录类型",
        max_length=32,
        choices=RecordType.choices,
        default=RecordType.OTHER,
    )
    title = models.CharField("记录标题", max_length=128)
    record_date = models.DateField("记录日期")
    next_remind_date = models.DateField("下次提醒日期", null=True, blank=True)
    hospital = models.CharField("医院", max_length=128, blank=True)
    doctor = models.CharField("医生", max_length=64, blank=True)
    cost = models.DecimalField(
        "费用",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    description = models.TextField("描述", blank=True)
    attachments = models.JSONField("附件", default=list, blank=True)

    class Meta:
        verbose_name = "健康记录"
        verbose_name_plural = "健康记录"
        ordering = ["-record_date", "-created_at"]
        indexes = [
            models.Index(fields=["pet"], name="pets_health_pet_idx"),
            models.Index(fields=["record_type"], name="pets_health_type_idx"),
            models.Index(fields=["next_remind_date"], name="pets_health_remind_idx"),
        ]

    def __str__(self):
        return f"{self.pet_id}-{self.title}"


class WeightRecord(models.Model):
    pet = models.ForeignKey(
        Pet,
        verbose_name="宠物",
        related_name="weight_records",
        on_delete=models.CASCADE,
    )
    weight = models.DecimalField("体重", max_digits=6, decimal_places=2)
    record_date = models.DateField("记录日期")
    remark = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "体重记录"
        verbose_name_plural = "体重记录"
        ordering = ["record_date", "created_at"]
        indexes = [
            models.Index(fields=["pet"], name="pets_weight_pet_idx"),
            models.Index(fields=["record_date"], name="pets_weight_date_idx"),
        ]

    def __str__(self):
        return f"{self.pet_id}-{self.weight}kg"
