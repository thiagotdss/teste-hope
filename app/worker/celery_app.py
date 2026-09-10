from celery import Celery

celery_app = Celery(
    "consulta_worker",
    broker="redis://redis:6379/0",
    include=["app.worker.tasks"],
)