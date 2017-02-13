import os

config = {
    "storage": {
        "hdfs": False,
        "localfs": True
    },
    "localfs": {
        "root_dir": "/srv/stat-data"
    },
    "rabbitmq": {
        "broker_url": os.getenv('RABBITMQ_BROKER_URL'),
        "exchange_name": os.getenv('RABBITMQ_EXCHANGE_NAME', 'stat_persistor_exchange_topic'),
        "auto_delete": os.getenv('RABBITMQ_AUTODELETE', False),
        "queue_name": os.getenv('RABBITMQ_QUEUE_NAME', 'stat_logger')
    },
    "logger": {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)5s] [%(process)5s] [%(name)10s] %(message)s"
            }
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "default"
            }
        },
        "loggers": {
            "stat_logger": {
                "handlers": ["default"],
                "level": os.getenv('LOG_LEVEL', 'INFO'),
                "propagate": True
            }
        }
    }
}
