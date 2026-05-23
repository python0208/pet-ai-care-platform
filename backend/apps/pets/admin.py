from django.contrib import admin

from apps.pets.models import HealthRecord, Pet, WeightRecord


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "species", "breed", "weight", "updated_at")
    list_filter = ("species", "gender", "neutered")
    search_fields = ("name", "breed", "owner__email")


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "pet", "record_type", "title", "record_date", "next_remind_date")
    list_filter = ("record_type", "record_date", "next_remind_date")
    search_fields = ("title", "pet__name", "hospital", "doctor")


@admin.register(WeightRecord)
class WeightRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "pet", "weight", "record_date", "created_at")
    list_filter = ("record_date",)
    search_fields = ("pet__name",)
