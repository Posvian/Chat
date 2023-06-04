import logging
import os
import sys

client_formatter = logging.Formatter('%(asctime)-30s %(levelname)-10s %(module)-20s %(message)s')

LOG_FILE_PATH = 'logs/client.log'
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, LOG_FILE_PATH)


critical_handler = logging.StreamHandler(sys.stderr)
critical_handler.setLevel(logging.CRITICAL)
critical_handler.setFormatter(client_formatter)

client_log_handler = logging.FileHandler(PATH, encoding='utf-8')
client_log_handler.setFormatter(client_formatter)


client_logger = logging.getLogger('Client')
client_logger.setLevel(logging.DEBUG)
client_logger.addHandler(critical_handler)
client_logger.addHandler(client_log_handler)


if __name__ == '__main__':
    client_logger.critical('Critical error')
    client_logger.debug('Debug')
    print(PATH)
