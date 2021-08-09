from json import load
from os import environ
# openssl rand -hex 32
try:
    with open('conf.json', 'r') as config_file:
        DEBUG = True
        secret_keys = load(config_file)

        # get yours! openssl rand -hex 32
        SECRET_KEY = secret_keys['SECRET_KEY']
        ALGORITHM = secret_keys.get("ALGORITHM")
        RABBITMQ_USER = secret_keys['RABBITMQ_USER']
        RABBITMQ_PASSWORD = secret_keys['RABBITMQ_PASSWORD']
        RABBITMQ_HOST_PORT = secret_keys['RABBITMQ_HOST_PORT']
        RABBITMQ_VHOST = secret_keys['RABBITMQ_VHOST']

except FileNotFoundError:

    #  TODO figure out why the server fails with debug set to false
    DEBUG = True

    SECRET_KEY = environ['SECRET_KEY']
    ALGORITHM = environ["ALGORITHM"]
    RABBITMQ_USER = environ['RABBITMQ_USER']
    RABBITMQ_PASSWORD = environ['RABBITMQ_PASSWORD']
    RABBITMQ_HOST_PORT = environ['RABBITMQ_HOST_PORT']
    RABBITMQ_VHOST = environ['RABBITMQ_VHOST']