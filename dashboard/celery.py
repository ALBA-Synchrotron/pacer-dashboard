import os
from celery import Celery
from kombu import Queue, Exchange

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

app: Celery = Celery("pacer-dashboard")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.task_queues: list = [
    Queue(
        'dashboard-logging',
        Exchange('dashboard-logging-exchange', type='direct'),
        routing_key='message.logging',
    ),
]

app.autodiscover_tasks()
