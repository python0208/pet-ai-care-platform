"""Celery application placeholder for later phases."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("pet_ai_care")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
