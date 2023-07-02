import sys
import logging
import log.server_log_config
import log.client_log_config
import traceback
import inspect

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('Server')
else:
    logger = logging.getLogger('Client')


def log(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        logger.debug(
            f'Была вызвана функция {func.__name__} , '
            f'была вызвана из функции {traceback.format_stack()[0].strip().split()[-1]}.'
            f'Вызов из модуля {func.__module__}.')

        return res

    return wrapper
