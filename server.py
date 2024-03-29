import argparse
import configparser
import os.path
import sys
import logging
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, MESSAGE, MESSAGE_TEXT, ERROR, \
    DEFAULT_PORT, SENDER, DESTINATION, EXIT, RESPONSE_202, LIST_INFO, GET_CONTACTS, ADD_CONTACT, \
    RESPONSE_200, REMOVE_CONTACT, USERS_REQUEST, RESPONSE_400
from decorators import log
from server.core import MessageProcessor
from server.main_window import MainWindow
from server.server_database import ServerStorage
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

server_logger = logging.getLogger('Server')


@log
def arg_parser(port, address):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=port, type=int, nargs='?')
    parser.add_argument('-a', default=address, nargs='?')
    parser.add_argument('--no_gui', action='store_true')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    gui_flag = namespace.no_gui
    return listen_address, listen_port, gui_flag


def config_load():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")

    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


def main():
    config = config_load()

    listen_address, listen_port, gui_flag = arg_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    if gui_flag:
        while True:
            command = input('Введите exit для завершения работы сервера.')
            if command == 'exit':
                server.running = False
                server.join()
                break

    else:
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)

        server_app.exec_()

        server.running = False


if __name__ == '__main__':
    main()
