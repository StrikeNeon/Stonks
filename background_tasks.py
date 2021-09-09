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

# TODO The whole rest api should be just task management
# endpoints:
#   data gathering,
#   ta computation and signaling,
#   banking operations,
#   strategic analysis
# custom task states are needed


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
def data_gathering_task(symbol: str, client: str, password: str, hour_interval: int):
    if not db_manager.active_clients.get(client):
        db_manager.add_client(client, password)
    if db_manager.get_current_data(symbol) == 404:
        db_manager.setup_symbol(symbol, client)
        celery_log.info(f"{symbol} has been set up")
    schedule.every(24).hours.do(db_manager.setup_symbol, symbol, client)
    schedule.every(hour_interval).hours.do(db_manager.add_symbol_tick, symbol, client, hour_interval)
    celery_log.info(f"{client} started gathering {symbol} data")
    while True:
        schedule.run_pending()
        sleep(hour_interval*pow(60, 2))
        celery_log.info(f"tick added to {symbol}")
    return {"message": f"{client} finished gathering {symbol} data"}

@celery.task()
def signaling_task(symbol: str, hour_interval: int, rsi_thresh: int):
    if db_manager.get_current_data(symbol) == 404:
        celery_log.info(f"{symbol} data empty, aborting")
        return {"message": f"{symbol} data empty, aborting"}

    schedule.every(hour_interval).hours.do(db_manager.write_last_signal, symbol, rsi_thresh)
    celery_log.info(f"started signaling {symbol}")
    while True:
        schedule.run_pending()
        sleep(hour_interval*pow(60, 2))
        celery_log.info(f"{symbol} signaling cycle")
    return {"message": f"finished signaling {symbol}"}

def stop_data_gathering(task_id: str):
    controller.revoke(task_id, terminate=True, signal='SIGTERM')
    return {"message": f"task {task_id} stopped"}
