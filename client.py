import sys
import json
from socket import *
import time


def make_presence(login='Guest'):
    out = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': login
        }
    }
    return out


def server_answer_parser(answer):
    if 'response' in answer:
        if answer['response'] == 200:
            return '200 : OK'
        return f'400 : {answer["error"]}'
    raise ValueError


def main():
    try:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_ip = '127.0.0.1'
        server_port = 7777
    except ValueError:
        print('Порт должен быть в диапазоне 1024 и 65535.')
        sys.exit(1)

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    client_massage = make_presence()
    json_massage = json.dumps(client_massage)
    json_massage_encoded = json_massage.encode('utf-8')
    client_socket.send(json_massage_encoded)

    json_answer_encoded = client_socket.recv(1000000)
    try:
        json_answer = json_answer_encoded.decode('utf-8')
        answer = server_answer_parser(json.loads(json_answer))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Декодирование сообщения прошло неуспешно!')


if __name__ == '__main__':
    main()





