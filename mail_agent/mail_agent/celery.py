import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mail_agent.settings")

app = Celery("mail_agent")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()