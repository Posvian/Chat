import argparse
import sys
import json
import time
from select import select
from socket import *
import logging
import log.server_log_config
from common.functions import send_message, get_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, MESSAGE, MESSAGE_TEXT, ERROR, \
    DEFAULT_PORT, MAX_CONNECTIONS, SENDER
from decorators import log

server_logger = logging.getLogger('Server')


@log
def client_message_varification(message, messages_list, client):
    server_logger.info('Идет верификация сообщения клиента')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad request'
        })
        return


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        server_logger.critical(f'Порт должен быть в диапазоне 1024 и 65535. '
                               f'Попытка запуска с портом {listen_port}')
        sys.exit(1)

    return listen_address, listen_port


def main():
    listen_address, listen_port = arg_parser()
    server_logger.info(f'Запущен сервер с параметрами {listen_address}: {listen_port}')

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((listen_address, listen_port))
    server_socket.settimeout(0.5)

    clients = []
    messages = []

    server_socket.listen(MAX_CONNECTIONS)
    while True:
        try:
            client, client_address = server_socket.accept()
        except OSError:
            pass
        else:
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []

        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    client_message_varification(get_message(client_with_message), messages, client_with_message)
                except:
                    server_logger.info(f'Клиент {client_with_message.getpeername()} отключился')
                    clients.remove(client_with_message)

        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for client in send_data_lst:
                try:
                    send_message(client, message)
                except:
                    server_logger.info(f'Клиент {client.getpeername()}')
                    clients.remove(client)


if __name__ == '__main__':
    main()
