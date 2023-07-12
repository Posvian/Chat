import sys
import logging
import log.server_log_config
import log.client_log_config
import traceback
import inspect
import socket

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


def login_required(func):
    def checker(*args, **kwargs):
        from server.core import MessageProcessor
        from common.variables import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker

