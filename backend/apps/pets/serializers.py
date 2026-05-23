from django.utils import timezone
from rest_framework import serializers

from apps.pets.models import HealthRecord, Pet, WeightRecord


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = (
            "id",
            "record_type",
            "title",
            "record_date",
            "next_remind_date",
            "hospital",
            "doctor",
            "cost",
            "description",
            "attachments",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_attachments(self, value):
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("attachments 必须是列表")
        return value


class WeightRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightRecord
        fields = ("id", "weight", "record_date", "remark", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("体重必须大于 0")
        return value


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = (
            "id",
            "name",
            "species",
            "breed",
            "gender",
            "birthday",
            "avatar",
            "color",
            "weight",
            "neutered",
            "remark",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_weight(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("体重必须大于 0")
        return value


class PetDetailSerializer(PetSerializer):
    latest_vaccine_record = serializers.SerializerMethodField()
    latest_deworm_record = serializers.SerializerMethodField()
    latest_weight_record = serializers.SerializerMethodField()
    reminders = serializers.SerializerMethodField()
    record_stats = serializers.SerializerMethodField()

    class Meta(PetSerializer.Meta):
        fields = PetSerializer.Meta.fields + (
            "latest_vaccine_record",
            "latest_deworm_record",
            "latest_weight_record",
            "reminders",
            "record_stats",
        )

    def get_latest_vaccine_record(self, obj):
        return self._latest_health_record(obj, HealthRecord.RecordType.VACCINE)

    def get_latest_deworm_record(self, obj):
        return self._latest_health_record(obj, HealthRecord.RecordType.DEWORM)

    def get_latest_weight_record(self, obj):
        record = obj.weight_records.order_by("-record_date", "-created_at").first()
        return WeightRecordSerializer(record).data if record else None

    def get_reminders(self, obj):
        today = timezone.localdate()
        records = (
            obj.health_records.filter(next_remind_date__isnull=False)
            .order_by("next_remind_date", "-record_date")
        )
        reminders = []
        seen_types = set()
        for record in records:
            if record.record_type in seen_types:
                continue
            seen_types.add(record.record_type)
            reminders.append(
                {
                    "record_type": record.record_type,
                    "title": record.title,
                    "next_remind_date": record.next_remind_date,
                    "days_until": (record.next_remind_date - today).days,
                }
            )
        return reminders

    def get_record_stats(self, obj):
        latest_deworm = obj.health_records.filter(
            record_type=HealthRecord.RecordType.DEWORM
        ).order_by("-record_date", "-created_at").first()
        return {
            "vaccine_count": obj.health_records.filter(
                record_type=HealthRecord.RecordType.VACCINE
            ).count(),
            "deworm_status": latest_deworm.title if latest_deworm else "",
            "current_weight": str(obj.weight) if obj.weight is not None else "",
        }

    def _latest_health_record(self, obj, record_type):
        record = obj.health_records.filter(record_type=record_type).first()
        return HealthRecordSerializer(record).data if record else None
