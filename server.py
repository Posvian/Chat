import argparse
import sys
import json
import threading
import time
from select import select
from socket import *
import logging
import log.server_log_config
from common.functions import send_message, get_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, MESSAGE, MESSAGE_TEXT, ERROR, \
    DEFAULT_PORT, MAX_CONNECTIONS, SENDER, DESTINATION, EXIT
from decorators import log
from descriptors import PortVerifier
from metaclasses import ServerVerifier
from server_database import ServerStorage

server_logger = logging.getLogger('Server')


class Server(threading.Thread, metaclass=ServerVerifier):
    port = PortVerifier('port')

    def __init__(self, listen_address, listen_port, database):
        self.address = listen_address
        self.port = listen_port

        self.database = database

        self.clients = []
        self.messages = []
        self.names = dict()

        super().__init__()

    def init_socket(self):
        server_logger.info(f'Запущен сервер с параметрами {self.address}: {self.port}')

        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind((self.address, self.port))
        server_socket.settimeout(0.5)

        self.socket = server_socket
        self.socket.listen()

    def message_to_destination(self, message, listening_sockets):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listening_sockets:
            send_message(self.names[message[DESTINATION]], message)
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listening_sockets:
            raise ConnectionError
        else:
            server_logger.error(f'Client {message[DESTINATION]} is not login.')

    def client_message_varification(self, message, client):
        server_logger.info('Идет верификация сообщения клиента')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, {RESPONSE: 200})
            else:
                response = {
                    RESPONSE: 400,
                    ERROR: 'Имя уже занято, прошу выбрать другое.'
                }
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return

        elif ACTION in message and message[ACTION] == MESSAGE and \
                DESTINATION in message and TIME in message and MESSAGE_TEXT in message and SENDER in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        else:
            send_message(client, {
                RESPONSE: 400,
                ERROR: 'Bad request'
            })
            return

    def run(self):
        self.init_socket()

        while True:
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.client_message_varification(get_message(client_with_message), client_with_message)
                    except:
                        server_logger.info(f'Клиент {client_with_message.getpeername()} отключился')
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.message_to_destination(message, send_data_lst)
                except:
                    server_logger.debug(f'connection with {message[DESTINATION]} was lost')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()


#
# @log
# def client_message_varification(message, messages_list, client, clients, names):
#     server_logger.info('Идет верификация сообщения клиента')
#     if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
#             and USER in message:
#         if message[USER][ACCOUNT_NAME] not in names.keys():
#             names[message[USER][ACCOUNT_NAME]] = client
#             send_message(client, {RESPONSE: 200})
#         else:
#             response = {
#                 RESPONSE: 400,
#                 ERROR: 'Имя уже занято, прошу выбрать другое.'
#             }
#             send_message(client, response)
#             clients.remove(client)
#             client.close()
#         return
#
#     elif ACTION in message and message[ACTION] == MESSAGE and \
#             DESTINATION in message and TIME in message and MESSAGE_TEXT in message and SENDER in message:
#         messages_list.append(message)
#         return
#     elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
#         clients.remove(names[message[ACCOUNT_NAME]])
#         names[message[ACCOUNT_NAME]].close()
#         del names[message[ACCOUNT_NAME]]
#         return
#     else:
#         send_message(client, {
#             RESPONSE: 400,
#             ERROR: 'Bad request'
#         })
#         return
#
#
# @log
# def message_to_destination(message, names, listening_sockets):
#     if message[DESTINATION] in names and names[message[DESTINATION]] in listening_sockets:
#         send_message(names[message[DESTINATION]], message)
#     elif message[DESTINATION] in names and names[message[DESTINATION]] not in listening_sockets:
#         raise ConnectionError
#     else:
#         server_logger.error(f'Client {message[DESTINATION]} is not login.')
#

@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


def print_help():
    print('Введите одну из команд:')
    print('users - список всех пользователей.')
    print('connected - список пользователей онлайн.')
    print('loging_history - история входов.')
    print('exit - завершение работы сервера.')
    print('help - повторный вывод подсказок.')


def main():
    listen_address, listen_port = arg_parser()

    database = ServerStorage()

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    print_help()

    while True:
        command = input('Введите команду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(database.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loging_history':
            name = input(
                'Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    main()
