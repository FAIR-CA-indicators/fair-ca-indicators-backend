from celery import Celery
from app.dependencies.settings import get_settings

config = get_settings()
# FIXME Need to load broker from settings
app = Celery("fair-combine", broker=config.celery_broker)
app.autodiscover_tasks(["app.celery.automated_tasks"])
