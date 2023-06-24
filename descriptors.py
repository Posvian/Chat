import logging

server_logger = logging.getLogger('Server')

class PortVerifier:
    def __init__(self, my_attr):
        self.my_attr = my_attr
    def __set__(self, instance, value):

        if not (1023 < value < 65536):
            server_logger.critical(f'Номер порта {value} выходит за допустимые значения!')
            exit(1)

        instance.__dict__[self.my_attr] = value
