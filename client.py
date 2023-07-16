import os.path
import sys
import logging
import argparse
from Cryptodome.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox

from common.variables import *
from common.errors import ServerError
from decorators import log
from client.client_database import ClientDatabase
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog

client_logger = logging.getLogger('Client')


@log
def arg_parser():
    """
    Функция - парсер аргументов командной строки.
    Возвращает список из 4-х аргументов.
    Также проверяет корректность номера порта.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-p', '--password', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_password = namespace.password


    if not 1023 < server_port < 65536:
        client_logger.critical(f'Порт должен быть в диапазоне 1024 и 65535. '
                               f'Попытка запуска с портом {server_port}')
        exit(1)

    return server_address, server_port, client_name, client_password


if __name__ == '__main__':
    server_address, server_port, client_name, client_password = arg_parser()

    client_app = QApplication(sys.argv)

    start_dialog = UserNameDialog()

    if not client_name or not client_password:
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_password = start_dialog.client_password.text()
        else:
            exit(0)

    client_logger.info(f'Запущен клиент с парамертами: '
                       f'адрес сервера: {server_address} , '
                       f'порт: {server_port}, '
                       f'имя пользователя: {client_name}'
                       )

    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    database = ClientDatabase(client_name)

    try:
        transport = ClientTransport(server_port, server_address, database, client_name, client_password, keys)
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Ошибка сервера', error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    del start_dialog

    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)

    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()




#
#
# class ClientSender(threading.Thread, metaclass=ClientVerifier):
#     def __init__(self, login, client_socket, database):
#         self.login = login
#         self.client_socket = client_socket
#         self.database = database
#         super().__init__()
#
#     def exit_message(self):
#         return {
#             ACTION: EXIT,
#             TIME: time.time(),
#             ACCOUNT_NAME: self.login
#         }
#
#     def create_message(self):
#         destination = input('Введите получателя сообщения: ')
#         message = input("Введите сообщение: ")
#
#         with database_lock:
#             if not self.database.check_user(destination):
#                 client_logger.error(f'Попытка отправить сообщение незарегистрированному получателю: {destination}')
#                 return
#
#         js_message = {
#             ACTION: MESSAGE,
#             SENDER: self.login,
#             DESTINATION: destination,
#             TIME: time.time(),
#             MESSAGE_TEXT: message
#         }
#         client_logger.debug(f'Сформировано сообщение: {js_message}')
#
#         with database_lock:
#             self.database.save_message(self.login, destination, message)
#
#         with sock_lock:
#             try:
#                 send_message(self.client_socket, js_message)
#                 client_logger.debug(f'{message} отправлено получателю {destination}')
#             except OSError as err:
#                 if err.errno:
#                     client_logger.critical('Потеряно соединение с сервером.')
#                     exit(1)
#                 else:
#                     client_logger.error('Не удалось передать сообщение. Таймаут соединения')
#
#     def run(self):
#         self.user_help()
#         while True:
#             command = input('Введите команду: ')
#             if command == 'exit':
#                 try:
#                     send_message(self.client_socket, self.exit_message())
#                 except:
#                     pass
#                 print('Завершаю соединение. Ждем Вас снова в нашем чате.')
#                 time.sleep(1)
#                 break
#             elif command == 'help':
#                 self.user_help()
#             elif command == 'message':
#                 self.create_message()
#             elif command == 'contacts':
#                 with database_lock:
#                     contacts_list = self.database.get_contacts()
#                 for contact in contacts_list:
#                     print(contact)
#             elif command == 'edit':
#                 self.edit_contacts()
#             elif command == 'history':
#                 self.print_history()
#             else:
#                 print('Такой команды нет, мы работаем над искусственным интеллектом, но пока введите "help"')
#
#     def user_help(self):
#         print('Выберите одну из команд:')
#         print('exit - выход;')
#         print('help - позвать на помощь;')
#         print('message - отправить сообщение.')
#         print('contacts - список контактов.')
#         print('history - история сообщений.')
#         print('edit - изменить список контактов.')
#
#     def print_history(self):
#         ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
#         with database_lock:
#             if ask == 'in':
#                 history_list = self.database.get_history(to_who=self.login)
#                 for message in history_list:
#                     print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
#             elif ask == 'out':
#                 history_list = self.database.get_history(from_who=self.login)
#                 for message in history_list:
#                     print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
#             else:
#                 history_list = self.database.get_history()
#                 for message in history_list:
#                     print(
#                         f'\nСообщение от пользователя: {message[0]}, пользователю {message[1]} от {message[3]}\n{message[2]}')
#
#     def edit_contacts(self):
#         ans = input('Для удаления введите del, для добавления add: ')
#         if ans == 'del':
#             edit = input('Введите имя удаляемого контакта: ')
#             with database_lock:
#                 if self.database.check_contact(edit):
#                     self.database.del_contact(edit)
#                 else:
#                     client_logger.error('Попытка удаления несуществующего контакта.')
#         elif ans == 'add':
#             # Проверка на возможность такого контакта
#             edit = input('Введите имя создаваемого контакта: ')
#             if self.database.check_user(edit):
#                 with database_lock:
#                     self.database.add_contact(edit)
#                 with sock_lock:
#                     try:
#                         add_contact(self.client_socket, self.login, edit)
#                     except Exception:
#                         client_logger.error('Не удалось отправить информацию на сервер.')
#
#
# class ClientReader(threading.Thread, metaclass=ClientVerifier):
#     def __init__(self, login, client_socket, database):
#         self.login = login
#         self.client_socket = client_socket
#         self.database = database
#         super().__init__()
#
#     def run(self):
#         while True:
#             time.sleep(1)
#             with sock_lock:
#                 try:
#                     message = get_message(self.client_socket)
#                 except json.JSONDecodeError:
#                     client_logger.error('Ошибка в декодировании сообщения')
#                 except OSError as err:
#                     if err.errno:
#                         client_logger.critical(f'Потеряно соединение с сервером.')
#                         break
#                 except (OSError, ConnectionResetError, ConnectionAbortedError, ConnectionError):
#                     client_logger.critical('потеряно соединение с сервером.')
#                     break
#                 else:
#                     if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
#                             and MESSAGE_TEXT in message and message[DESTINATION] == self.login:
#                         print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
#                         # Захватываем работу с базой данных и сохраняем в неё сообщение
#                         with database_lock:
#                             try:
#                                 self.database.save_message(message[SENDER], self.login, message[MESSAGE_TEXT])
#                             except:
#                                 client_logger.error('Ошибка взаимодействия с базой данных')
#
#                         client_logger.info(
#                             f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
#                     else:
#                         client_logger.error(f'Получено некорректное сообщение с сервера: {message}')
#
#
# @log
# def make_presence(login):
#     out = {
#         ACTION: PRESENCE,
#         TIME: time.time(),
#         USER: {
#             ACCOUNT_NAME: login
#         }
#     }
#     client_logger.debug(f'Формируем сообщение для пользователя {login}')
#     return out
#
#
# @log
# def server_answer_parser(answer):
#     if RESPONSE in answer:
#         if answer[RESPONSE] == 200:
#             client_logger.debug(f'Корректное сообщение от сервера')
#             return '200 : OK'
#         client_logger.error(f'400 : {answer[ERROR]}')
#         return f'400 : {answer[ERROR]}'
#     client_logger.critical(f'Неверный ответ сервера {answer}')
#     raise ValueError
#
#
#
# def contacts_request(client_socket, name):
#     client_logger.debug(f'запрос листа контактов для пользователя {name}')
#     request = {
#         ACTION: GET_CONTACTS,
#         TIME: time.time(),
#         USER: name
#     }
#     client_logger.debug(f'{request} - запрос.')
#     send_message(client_socket, request)
#     answer = get_message(client_socket)
#     client_logger.debug(f'{answer} - ответ.')
#     if RESPONSE in answer and answer[RESPONSE] == 202:
#         return answer[LIST_INFO]
#     else:
#         raise ValueError
#
#
# def add_contact(client_socket, login, contact):
#     client_logger.debug(f'{contact} - контакт для создания')
#     request = {
#         ACTION: ADD_CONTACT,
#         TIME: time.time(),
#         USER: login,
#         ACCOUNT_NAME: contact
#     }
#     send_message(client_socket, request)
#     answer = get_message(client_socket)
#     if RESPONSE in answer and answer[RESPONSE] == 200:
#         pass
#     else:
#         raise ValueError('Контакт не создан')
#     print('Контакт создан удачно.')
#
#
# def known_user_list_request(client_socket, login):
#     client_logger.debug(f'Запрос списка известных пользователей {login}')
#     request = {
#         ACTION: USERS_REQUEST,
#         TIME: time.time(),
#         ACCOUNT_NAME: login
#     }
#     send_message(client_socket, request)
#     answer = get_message(client_socket)
#     if RESPONSE in answer and answer[RESPONSE] == 202:
#         return answer[LIST_INFO]
#     else:
#         raise ValueError
#
#
# def remove_contact(client_socket, login, contact):
#     client_logger.debug(f'Удаляю контакт - {contact}.')
#     request = {
#         ACTION: REMOVE_CONTACT,
#         TIME: time.time(),
#         USER: login,
#         ACCOUNT_NAME: contact
#     }
#     send_message(client_socket, request)
#     answer = get_message(client_socket)
#     if RESPONSE in answer and answer[RESPONSE] == 200:
#         pass
#     else:
#         raise ValueError('Ошибка удаления клиента')
#     print('Done!')
#
#
# def database_load(client_socket, database, login):
#     try:
#         list_of_users = known_user_list_request(client_socket, login)
#     except ValueError:
#         client_logger.error('Ошибка запроса списка известных пользователей.')
#     else:
#         database.add_users(list_of_users)
#
#     try:
#         list_of_contacts = contacts_request(client_socket, login)
#     except ValueError:
#         client_logger.error('Ошибка запроса списка контактов.')
#     else:
#         for contact in list_of_contacts:
#             database.add_contact(contact)
#
#
# def main():
#     print('Client mode')
#     server_address, server_port, client_name = arg_parser()
#     if not client_name:
#         client_name = input('Введите свое имя: ')
#     else:
#         print(f'Вы зашли под именем {client_name}')
#
#     try:
#         transport = socket(AF_INET, SOCK_STREAM)
#         transport.settimeout(1)
#
#         transport.connect((server_address, server_port))
#         send_message(transport, make_presence(client_name))
#         answer = server_answer_parser(get_message(transport))
#         client_logger.info(f'Установлено соединение, получен ответ {answer}')
#         print('Установлено соединение с сервером.')
#     except json.JSONDecodeError:
#         client_logger.error('Не удалось декодировать полученную строку.')
#         exit(1)
#     except ValueError:
#         client_logger.error(f'В ответе присутствуют не все поля.')
#         exit(1)
#     except (ConnectionRefusedError, ConnectionError):
#         client_logger.critical(
#             f'Не удалось подключиться к серверу {server_address}:{server_port}.'
#         )
#         exit(1)
#     else:
#         database = ClientDatabase(client_name)
#         database_load(transport, database, client_name)
#
#         user_interface = ClientSender(client_name, transport, database)
#         user_interface.daemon = True
#         user_interface.start()
#         client_logger.info('Processes start.')
#
#         receiver = ClientReader(client_name, transport, database)
#         receiver.daemon = True
#         receiver.start()
#
#         while True:
#             time.sleep(1)
#             if receiver.is_alive() and user_interface.is_alive():
#                 continue
#             break
#
#
# if __name__ == '__main__':
#     main()
