import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QDialog, QPushButton, \
    QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
import os


def gui_create_model(db):
    users_list = db.active_users_list()
    gui_list = QStandardItemModel()
    gui_list.setHorizontalHeaderLabels(['Login', 'IP address', 'Port', 'Connection time'])
    for row in users_list:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        gui_list.appendRow([user, ip, port, time])
    return gui_list


def create_stat_model(db):
    message_history = db.message_history()
    gui_list = QStandardItemModel()
    gui_list.setHorizontalHeaderLabels(
        ['Login', 'Last login', 'Send message count', 'Input message count'])
    for row in message_history:
        user, last_seen, sent, input = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        sent = QStandardItem(str(sent))
        sent.setEditable(False)
        input = QStandardItem(str(input))
        input.setEditable(False)
        gui_list.appendRow([user, last_seen, sent, input])
    return gui_list



class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Client statistics')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()


