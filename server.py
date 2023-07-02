import argparse
import configparser
import os.path
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
    DEFAULT_PORT, MAX_CONNECTIONS, SENDER, DESTINATION, EXIT, RESPONSE_202, LIST_INFO, GET_CONTACTS, ADD_CONTACT, \
    RESPONSE_200, REMOVE_CONTACT, USERS_REQUEST
from decorators import log
from descriptors import PortVerifier
from metaclasses import ServerVerifier
from server_database import ServerStorage
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_stat_model, ConfigWindow
from PyQt5.QtGui import QStandardItemModel, QStandardItem

server_logger = logging.getLogger('Server')

new_connection = False
conflag_lock = threading.Lock()


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
        global new_connection
        server_logger.info('Идет верификация сообщения клиента')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, {RESPONSE: 200})
                with conflag_lock:
                    new_connection = True
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
                DESTINATION in message and TIME in message and MESSAGE_TEXT in message and SENDER in message and \
                self.names[message[SENDER]] == client:
            self.messages.append(message)
            self.database.process_message(
                message[SENDER], message[DESTINATION]
            )
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            with conflag_lock:
                new_connection = True
            return

        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message and \
                self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            send_message(client, response)

        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)

        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)

        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0]
                                   for user in self.database.users_list()]
            send_message(client, response)

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
                        for name in self.names:
                            if self.names[name] == client_with_message:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.message_to_destination(message, send_data_lst)
                except (ConnectionAbortedError, ConnectionError, ConnectionResetError, ConnectionRefusedError):
                    server_logger.debug(f'connection with {message[DESTINATION]} was lost')
                    self.clients.remove(self.names[message[DESTINATION]])
                    self.database.user_logout(message[DESTINATION])
                    del self.names[message[DESTINATION]]
            self.messages.clear()


@log
def arg_parser(port, address):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=port, type=int, nargs='?')
    parser.add_argument('-a', default=address, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


# def print_help():
#     print('Введите одну из команд:')
#     print('users - список всех пользователей.')
#     print('connected - список пользователей онлайн.')
#     print('loging_history - история входов.')
#     print('exit - завершение работы сервера.')
#     print('help - повторный вывод подсказок.')


def main():
    config = configparser.ConfigParser()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")

    listen_address, listen_port = arg_parser(config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.statusBar().showMessage('Server Working')
    main_window.active_clients_table.setModel(gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(
                        config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(
                    config_window,
                    'Ошибка',
                    'Порт должен быть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec_()
    #
    # while True:
    #     command = input('Введите команду: ')
    #     if command == 'help':
    #         print_help()
    #     elif command == 'exit':
    #         break
    #     elif command == 'users':
    #         for user in sorted(database.users_list()):
    #             print(f'Пользователь {user[0]}, последний вход: {user[1]}')
    #     elif command == 'connected':
    #         for user in sorted(database.active_users_list()):
    #             print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
    #     elif command == 'loging_history':
    #         name = input(
    #             'Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
    #         for user in sorted(database.login_history(name)):
    #             print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
    #     else:
    #         print('Команда не распознана.')


if __name__ == '__main__':
    main()
