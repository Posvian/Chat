import sys
import logging.handlers
import os

server_formatter = logging.Formatter('%(asctime)-30s %(levelname)-10s %(module)-20s %(message)s')

LOG_FILE_PATH = 'logs/server.log'
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, LOG_FILE_PATH)

critical_handler = logging.StreamHandler(sys.stderr)
critical_handler.setLevel(logging.CRITICAL)
critical_handler.setFormatter(server_formatter)

server_log_handler = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='midnight')
server_log_handler.setFormatter(server_formatter)

server_logger = logging.getLogger('Server')
server_logger.setLevel(logging.DEBUG)
server_logger.addHandler(critical_handler)
server_logger.addHandler(server_log_handler)

if __name__ == '__main__':
    server_logger.critical('Critical error')
    server_logger.debug('Debug')
