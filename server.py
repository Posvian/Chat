import sys
import json
from socket import *
import logging
import log.server_log_config
from decorators import log

server_logger = logging.getLogger('Server')

@log
def client_message_varification(message):
    server_logger.info('Идет верификация сообщения клиента')
    if 'action' in message and message['action'] == 'presence' and 'time' in message \
            and 'user' in message and message['user']['account_name'] == 'Guest':
        server_logger.debug('успешное подключение')
        return {'response' : 200}
    server_logger.error('подключение не прошло, ошибка в сообщении!')
    return {
        'response': 400,
        'error': 'Bad request'
    }


def main():
    try:
        if '-p' in sys.argv:
            server_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            server_port = 7777
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_logger.error('Нет номера порта после индекса -р')
        sys.exit(1)
    except ValueError:
        server_logger.error('Значение номера порта выходит из диапазона допустимых.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            server_ip = sys.argv[sys.argv.index('-a') +1]
        else:
            server_ip = ''
    except IndexError:
        server_logger.error('нет номера порта после индекса -а')
        sys.exit(1)

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((server_ip, server_port))

    server_socket.listen(5)

    while True:
        client, addr = server_socket.accept()
        data = client.recv(1000000)
        try:
            json_message = data.decode('utf-8')
            message = json.loads(json_message)
            print(message)
            server_logger.debug(f'Сообщение получено: {message}')
            response = client_message_varification(message)

            js_responce = json.dumps(response)
            encoded_responce = js_responce.encode('utf-8')
            client.send(encoded_responce)
            client.close()
        except (json.JSONDecodeError):
            server_logger.error('Некорректное сообщение от клиента')
            client.close()


if __name__ == '__main__':
    main()

