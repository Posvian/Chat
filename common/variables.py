
DEFAULT_PORT = 7777
DEFAULT_IP_ADRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'
SERVER_CONFIG = 'server.ini'

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'
DESTINATION = 'to'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'

SERVER_DATABASE = 'sqlite:///server_base.db3'

RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO:None
                }

RESPONSE_200 = {RESPONSE: 200}

RESPONSE_400 = {
            RESPONSE: 400,
            ERROR: None
        }

