import asyncio
import os
import time

from celery import Celery
from celery.result import AsyncResult
from .dependencies import DependenciesTask

os.environ.setdefault("C_FORCE_ROOT", "true")
celery = Celery(__name__)

celery.conf.update(
    CELERY_ACCEPT_CONTENT=["json", "pickle"],
    CELERY_RESULT_SERIALIZER="pickle",
)


@celery.task(name="training_model_task")
def training_model_task(
    **data_in,
) -> None:
    asyncio.run(
        DependenciesTask.save_trained_model(
            data_in=data_in,
        )
    )
