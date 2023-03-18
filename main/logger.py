import logging
import logging.config

from main.settings import Config


LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            "format": "%(levelname)s [%(name)s:%(process)d:%(lineno)d] %(asctime)s %(message)s",
        },
    },
    'handlers': {
        'console': {
            'formatter': "default",
            'class': "logging.StreamHandler",
            'stream': "ext://sys.stdout"
        }
    },
    'loggers': {
        '': {
            'level': Config.LOG_LEVEL,
            'handlers': ['console']
        },
        'flask_app': {
            'level': Config.LOG_LEVEL,
            'handlers': ['console'],
            'propagate': False
        },
        'file_sender_client': {
            'level': Config.FILE_SENDER_CLIENT.log_level,
            'handlers': ['console'],
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOG_CONFIG)
