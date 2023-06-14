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
    DEFAULT_PORT, MAX_CONNECTIONS, SENDER, DESTINATION, EXIT
from decorators import log

server_logger = logging.getLogger('Server')


@log
def client_message_varification(message, messages_list, client, clients, names):
    server_logger.info('Идет верификация сообщения клиента')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200})
        else:
            response = {
                RESPONSE: 400,
                ERROR: 'Имя уже занято, прошу выбрать другое.'
            }
            send_message(client, response)
            clients.remove(client)
            client.close()
        return

    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message and MESSAGE_TEXT in message and SENDER in message:
        messages_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad request'
        })
        return


@log
def message_to_destination(message, names, listening_sockets):
    if message[DESTINATION] in names and names[message[DESTINATION]] in listening_sockets:
        send_message(names[message[DESTINATION]], message)
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listening_sockets:
        raise ConnectionError
    else:
        server_logger.error(f'Client {message[DESTINATION]} is not login.')


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

    names = dict()

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
                    client_message_varification(get_message(client_with_message), messages, client_with_message,
                                                clients, names)
                except Exception:
                    server_logger.info(f'Клиент {client_with_message.getpeername()} отключился')
                    clients.remove(client_with_message)

        for message in messages:
            try:
                message_to_destination(message, names, send_data_lst)
            except Exception:
                server_logger.debug(f'connection with {message[DESTINATION]} was lost')
                clients.remove(names[message[DESTINATION]])
                del names[message[DESTINATION]]
        messages.clear()

if __name__ == '__main__':
    main()
