from celery import Celery


# FIXME Need to load broker from settings
app = Celery("fair-combine", broker="redis://localhost:6379/0")
app.autodiscover_tasks(["app.celery.automated_tasks"])
