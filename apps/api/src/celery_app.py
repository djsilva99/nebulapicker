import os

from celery import Celery
from src.configs.settings import Settings

settings: Settings = Settings()

celery_app = Celery(
    "nebulapicker",
    broker=os.getenv(
        settings.CELERY_BROKER_URL,
        "redis://localhost:6379/0",
    ),
)

celery_app.conf.update(
    worker_prefetch_multiplier=1,
)

celery_app.conf.imports = (
    "src.tasks",
)
