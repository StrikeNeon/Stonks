from celery import Celery
from celery.utils.log import get_task_logger
from settings import (RABBITMQ_USER,
                    RABBITMQ_PASSWORD, RABBITMQ_HOST_PORT,
                    RABBITMQ_VHOST)
from rest_api import db_manager

# Create the celery app and get the logger
celery = Celery('trader_tasks', broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST_PORT}/{RABBITMQ_VHOST}')
celery.conf.update(task_track_started=True,
                   worker_concurrency=1,
                   result_backend='mongodb://127.0.0.1:27017/',
                   mongodb_backend_settings={'database': 'stonks',
                                             'taskmeta_collection': 'taskmeta_collection'})
celery_log = get_task_logger(__name__)


@celery.task()
def data_gathering_task(symbol: str, client: str):
    db_manager.gather_data(symbol, client)
    celery_log.info(f"scrape of boards {boards} started for {username}")
    return {"message": f"{client} finished gathering {symbol} data"}
