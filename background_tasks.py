from celery import Celery
from celery.utils.log import get_task_logger
from settings import (RABBITMQ_USER,
                      RABBITMQ_PASSWORD,
                      RABBITMQ_HOST_PORT,
                      RABBITMQ_VHOST)
from db_utils import MongoManager
from celery.app.control import Control
import schedule
from time import sleep


db_manager = MongoManager()
# Create the celery app and get the logger
celery = Celery('trader_tasks', broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST_PORT}/{RABBITMQ_VHOST}')
celery.conf.update(task_track_started=True,
                   worker_concurrency=1,
                   result_backend='mongodb://127.0.0.1:27017/',
                   mongodb_backend_settings={'database': 'stonks',
                                             'taskmeta_collection': 'taskmeta_collection'})
controller = Control(celery)
celery_log = get_task_logger(__name__)


@celery.task()
def data_gathering_task(symbol: str, client: str, password: str, minute_interval: int):
    db_manager.add_client(client, password)
    celery_log.info(db_manager.active_clients)
    if db_manager.get_current_data(symbol) == 404:
        db_manager.setup_symbol(symbol, client)
        celery_log.info(f"{symbol} has been set up")
    schedule.every(24).hours.do(db_manager.setup_symbol, symbol, client)
    schedule.every(minute_interval).minutes.do(db_manager.add_symbol_tick, symbol, client)
    celery_log.info(f"{client} started gathering {symbol} data")
    while True:
        schedule.run_pending()
        sleep(minute_interval*60)
        celery_log.info(f"tick added to {symbol}")
    return {"message": f"{client} finished gathering {symbol} data"}


def stop_data_gathering(task_id: str):
    controller.revoke(task_id, terminate=True, signal='SIGTERM')
    return {"message": f"task {task_id} stopped"}
