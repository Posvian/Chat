import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from decorators import log


@log
def get_message(client):
    encoded_message = client.recv(MAX_PACKAGE_LENGTH)
    if type(encoded_message) == bytes:
        json_message = encoded_message.decode(ENCODING)
        message = json.loads(json_message)
        if type(message) == dict:
            return message
        raise ValueError
    raise ValueError


@log
def send_message(socket, message):
    if type(message) != dict:
        raise ValueError
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    socket.send(encoded_message)
