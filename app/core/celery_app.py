from celery import Celery
from app.config import settings

# create celery app
# broker -> redis receives tasks from FastAPI
# backend -> redis stores task results

celery_app = Celery(
    "docquery",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# celery configuration 
celery_app.conf.update(
    # task will retry if it fails 
    task_acks_late=True,
    # one task per worker at a time 
    worker_prefetch_multiplier=1,
)
