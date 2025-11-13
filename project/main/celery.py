import os

from celery import Celery
import multiprocessing

from celery.schedules import crontab

# import os
# os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
# os.environ["TOKENIZERS_PARALLELISM"] = "false"
multiprocessing.set_start_method("spawn", force=True)
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.dev')
app = Celery('main')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "update-expiry-status-daily": {
        "task": "neksio_api.tasks.assign_expired_user_group",
        "schedule": 120.0,
    },
}
