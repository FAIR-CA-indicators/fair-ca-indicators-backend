from celery import Celery
from .tasks import (
    f1_model_persistent_identifier,
)

#FIXME Need to load broker from settings
celery_app = Celery("fair-combine", broker="redis://localhost:6379/0", include=["app.models.automated_tasks.tasks"])


