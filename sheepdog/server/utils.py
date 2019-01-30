import logging
import sys

from loguru import logger

from sheepdog.conf import Conf


def init_logging(conf: Conf):
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelno, record.getMessage())

    access_log = logging.getLogger('aiohttp.access')
    access_log.setLevel(conf.log_level)
    access_log.addHandler(InterceptHandler())
    config = {
        'handlers': [{'sink': sys.stdout, 'level': conf.log_level, 'colorize': True}],
    }
    if conf.log_file:
        config['handlers'].append({'sink': conf.log_file, 'level': conf.log_level})
    logger.configure(**config)
