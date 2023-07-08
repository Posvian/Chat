from socket import AF_INET, SOCK_STREAM, socket
import time
import logging
import json
import threading
from PyQt5.QtCore import pyqtSignal, QObject

from common.functions import *
from common.variables import *
from common.errors import *

client_logger = logging.getLogger('Client')
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        self.transport = None
        self.connection_init(port, ip_address)

        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                client_logger.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            client_logger.error('Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            client_logger.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
        self.running = True

    def connection_init(self, port, ip_address):
        self.transport = socket(AF_INET, SOCK_STREAM)
        self.transport.settimeout(5)

        connected = False
        for i in range(5):
            client_logger.info(f'{i}-я попытка подключения.')
            try:
                self.transport.connect((ip_address, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        if not connected:
            client_logger.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')

        client_logger.debug('Установлено соединение с сервером')

        try:
            with socket_lock:
                send_message(self.transport, self.make_presence())
                self.server_answer_parser(get_message(self.transport))
        except (OSError, json.JSONDecodeError):
            client_logger.critical('Потеряно соединение с сервером тут!')
            raise ServerError('Потеряно соединение с сервером!')

    def make_presence(self):
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        client_logger.debug(f'Формируем сообщение для пользователя {self.username}')
        return out

    def server_answer_parser(self, answer):
        if RESPONSE in answer:
            if answer[RESPONSE] == 200:
                client_logger.debug(f'Корректное сообщение от сервера')
                return
            elif answer[RESPONSE] == 400:
                raise ServerError(f'{answer[ERROR]}')
            else:
                client_logger.debug(f'Принят неизвестный код подтверждения {answer[RESPONSE]}')

        elif ACTION in answer and answer[ACTION] == MESSAGE and SENDER in answer and DESTINATION in answer \
                and MESSAGE_TEXT in answer and answer[DESTINATION] == self.username:
            client_logger.debug(f'Получено сообщение от пользователя {answer[SENDER]}:{answer[MESSAGE_TEXT]}')
            self.database.save_message(answer[SENDER] , 'in' , answer[MESSAGE_TEXT])
            self.new_message.emit(answer[SENDER])

    def contacts_list_update(self):
        client_logger.debug(f'Запрос контакт листа для пользователся {self.name}')
        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        client_logger.debug(f'Сформирован запрос {request}')
        with socket_lock:
            send_message(self.transport, request)
            answer = get_message(self.transport)
        client_logger.debug(f'Получен ответ {answer}')
        if RESPONSE in answer and answer[RESPONSE] == 202:
            for contact in answer[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            client_logger.error('Не удалось обновить список контактов.')

    def user_list_update(self):
        client_logger.debug(f'Запрос списка известных пользователей {self.username}')
        request = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.transport, request)
            answer = get_message(self.transport)
        if RESPONSE in answer and answer[RESPONSE] == 202:
            self.database.add_users(answer[LIST_INFO])
        else:
            client_logger.error('Не удалось обновить список известных пользователей.')

    def add_contact(self, contact):
        client_logger.debug(f'Создание контакта {contact}')
        request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, request)
            self.server_answer_parser(get_message(self.transport))

    def remove_contact(self, contact):
        client_logger.debug(f'Удаление контакта {contact}')
        request = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, request)
            self.server_answer_parser(get_message(self.transport))

    def transport_shutdown(self):
        self.running = False
        request = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, request)
            except OSError:
                pass
        client_logger.debug('Сокет завершает работу.')
        time.sleep(0.5)

    def send_message(self, destination, message):
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: destination,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')

        with socket_lock:
            send_message(self.transport, message_dict)
            self.server_answer_parser(get_message(self.transport))
            client_logger.info(f'Отправлено сообщение для пользователя {destination}')

    def run(self):
        client_logger.debug('Запущен процесс - приёмник сообщений с сервера.')
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        client_logger.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    client_logger.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    client_logger.debug(f'Принято сообщение с сервера: {message}')
                    self.server_answer_parser(message)
                finally:
                    self.transport.settimeout(5)
