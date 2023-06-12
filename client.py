import socket
import sys
import json
from socket import *
import time
import logging
import argparse
import log.client_log_config
from common.functions import get_message, send_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, SENDER, MESSAGE_TEXT, \
    DEFAULT_IP_ADRESS, DEFAULT_PORT
from decorators import log

client_logger = logging.getLogger('Client')


@log
def message_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
        print(f'Пользователь {message[SENDER]} отправил сообщение {message[MESSAGE_TEXT]}')
    else:
        client_logger.error(f'{message} - некорректное сообщение!!!')


@log
def create_message(my_socket, login='Guest'):
    message = input("Введите сообщение (для завершения работы введите 'exit': ")
    if message == 'exit':
        my_socket.close()
        print('Надеюсь Вам понравился наш сервис, ждем Вашего скорейшего возвращения.')
        sys.exit(0)
    js_message = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: login,
        MESSAGE_TEXT: message
    }
    client_logger.debug(f'Сформировано сообщение: {js_message}')
    return js_message


@log
def make_presence(login='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: login
        }
    }
    client_logger.debug(f'Формируем сообщение для пользователя {login}')
    return out


@log
def server_answer_parser(answer):
    if RESPONSE in answer:
        if answer[RESPONSE] == 200:
            client_logger.debug(f'Корректное сообщение от сервера')
            return '200 : OK'
        client_logger.error(f'400 : {answer[ERROR]}')
        return f'400 : {answer[ERROR]}'
    client_logger.critical(f'Неверный ответ сервера {answer}')
    raise ValueError


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        client_logger.critical(f'Порт должен быть в диапазоне 1024 и 65535. '
                               f'Попытка запуска с портом {server_port}')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        client_logger.critical(f'запуск с недопустимым режимом {client_mode}')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    server_address, server_port, client_mode = arg_parser()
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        send_message(client_socket, make_presence())
        answer = server_answer_parser(get_message(client_socket))
        client_logger.info(f'Установлено соединение, получен ответ {answer}')
        print('Установлено соединение с сервером.')
    except json.JSONDecodeError:
        client_logger.error('Не удалось декодировать полученную строку.')
        sys.exit(1)
    except ValueError:
        client_logger.error(f'В ответе присутствуют не все поля.')
        sys.exit(1)
    except ConnectionRefusedError:
        client_logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}.'
        )
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('Выбран режим отправки сообщений')
        else:
            print('Выбран режим приема сообщений')
        while True:
            if client_mode == 'send':
                try:
                    send_message(client_socket, create_message(client_socket))
                except (ConnectionError, ConnectionResetError, ConnectionAbortedError):
                    client_logger.error(f'Connection with server {server_address} was lost.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    message_from_server(get_message(client_socket))
                except (ConnectionError, ConnectionResetError, ConnectionAbortedError):
                    client_logger.error(f'Connection with server {server_address} was lost.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
