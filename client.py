import socket
import sys
import json
import threading
from socket import *
import time
import logging
import argparse
import log.client_log_config
from common.functions import get_message, send_message
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, SENDER, MESSAGE_TEXT, \
    DEFAULT_IP_ADRESS, DEFAULT_PORT, EXIT, DESTINATION
from decorators import log

client_logger = logging.getLogger('Client')


@log
def exit_message(login):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: login
    }


@log
def message_from_server(server_socket, login):
    while True:
        try:
            message = get_message(server_socket)
            if ACTION in message and message[
                ACTION] == MESSAGE and SENDER in message and DESTINATION in message and MESSAGE_TEXT in message and \
                    message[DESTINATION] == login:
                print(f'Пользователь {message[SENDER]} отправил сообщение {message[MESSAGE_TEXT]}')
            else:
                client_logger.error(f'{message} - некорректное сообщение!!!')
        except json.JSONDecodeError:
            client_logger.error('Ошибка в декодировании сообщения')
        except (OSError, ConnectionResetError, ConnectionAbortedError, ConnectionError):
            client_logger.critical('потеряно соединение с сервером.')
            break


@log
def create_message(my_socket, login='Guest'):
    destination = input('Введите получателя сообщения: ')
    message = input("Введите сообщение: ")
    js_message = {
        ACTION: MESSAGE,
        SENDER: login,
        DESTINATION: destination,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    client_logger.debug(f'Сформировано сообщение: {js_message}')
    try:
        send_message(my_socket, js_message)
        client_logger.debug(f'{message} отправлено получателю {destination}')
    except:
        client_logger.debug('Потеряно соединение с сервером.')
        sys.exit(1)


@log
def user_help():
    print('Выберите одну из команд:')
    print('exit - выход;')
    print('help - позвать на помощь;')
    print('message - отправить сообщение.')


@log
def menu(server_socket, login):
    user_help()
    while True:
        command = input('Введите команду: ')
        if command == 'exit':
            send_message(server_socket, exit_message(login))
            print('Завершаю соединение. Ждем Вас снова в нашем чате.')
            time.sleep(1)
            break
        elif command == 'help':
            user_help()
        elif command == 'message':
            create_message(server_socket, login)
        else:
            print('Такой команды нет, мы работаем над искусственным интеллектом, но пока введите "help"')



@log
def make_presence(login):
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
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        client_logger.critical(f'Порт должен быть в диапазоне 1024 и 65535. '
                               f'Попытка запуска с портом {server_port}')
        sys.exit(1)

    return server_address, server_port, client_name


def main():
    print('Client mode')
    server_address, server_port, client_name = arg_parser()
    if not client_name:
        client_name = input('Введите свое имя: ')

    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        send_message(client_socket, make_presence(client_name))
        answer = server_answer_parser(get_message(client_socket))
        client_logger.info(f'Установлено соединение, получен ответ {answer}')
        print('Установлено соединение с сервером.')
    except json.JSONDecodeError:
        client_logger.error('Не удалось декодировать полученную строку.')
        sys.exit(1)
    except ValueError:
        client_logger.error(f'В ответе присутствуют не все поля.')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        client_logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}.'
        )
        sys.exit(1)
    else:
        receiver = threading.Thread(target=message_from_server, args=(client_socket, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=menu, args=(client_socket, client_name))
        user_interface.daemon = True
        user_interface.start()
        client_logger.info('Processes start.')

        while True:
            time.sleep(2)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
