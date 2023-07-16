import os

from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from common.variables import *
import datetime


class ClientDatabase:
    """
    Класс оболочка для работы с базой данных клиента.
    Построена на SQLite, реализована с помощью SQLAlchemy ORM
    с использованием классического подхода.
    """

    class KnownUsers:
        """
        Класс - отображение для таблицы всех пользователей.
        """

        def __init__(self, user):
            self.id = None
            self.username = user

    class MessageHistory:
        """
        Класс - отображение для таблицы истории сообщений.
        """

        def __init__(self, contact, direction, message):
            self.id = None
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts:
        """
        Класс - отображение для таблицы контактов.
        """
        def __init__(self, contact):
            self.id = None
            self.name = contact

    def __init__(self, name):
        path = os.path.dirname(os.path.realpath(__file__))
        filename = f'client_{name}.db3'
        self.database_engine = create_engine(f'sqlite:///{os.path.join(path, filename)}', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})

        self.metadata = MetaData()

        known_users = Table(
            'known_users',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String)
        )

        message_history = Table(
            'message_history',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('contact', String),
            Column('direction', String),
            Column('message', Text),
            Column('date', DateTime)
        )

        user_contacts = Table(
            'contacts',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String, unique=True)
        )

        self.metadata.create_all(self.database_engine)

        mapper(self.KnownUsers, known_users)
        mapper(self.MessageHistory, message_history)
        mapper(self.Contacts, user_contacts)

        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """
        Метод для добавления контактов в базу данных.
        """
        if not self.session.query(self.Contacts).filter_by(name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def contacts_clear(self):
        """
        Метод очищающий таблицу со списком контактов.
        """
        self.session.query(self.Contacts).delete()

    def del_contact(self, contact):
        """
        Метод для удаления контакта из базы данных.
        """
        self.session.query(self.Contacts).filter_by(name=contact).delete()

    def add_users(self, users_list):
        """
        Метод заполняющий таблицу известных пользователей.
        """
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, contact, direction, message):
        """
        Метод сохраняющий сообщения в базе данных
        """
        message_row = self.MessageHistory(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        """
        Метод возвращающий список всех контактов.
        """
        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        """
        Метод возвращающий список всех пользователей.
        """
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user):
        """
        Метод проверяющий существует ли пользователь.
        """
        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        """
        Метод проверяющий существует ли контакт.
        """
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact):
        """
        Метод возвращающий историю сообщений с определенным пользователем.
        """
        query = self.session.query(self.MessageHistory).filter_by(contact=contact)
        return [(history_row.contact, history_row.direction, history_row.message, history_row.date)
                for history_row in query.all()]


if __name__ == '__main__':
    test_db = ClientDatabase('Client1')
    for i in ['Contact1', 'Contact2', 'Contact3']:
        test_db.add_contact(i)
    test_db.add_contact('Contact4')
    test_db.add_users(['Client1', 'Contact2', 'Contact3', 'Contact4', 'Contact5'])
    test_db.save_message('Client1', 'Contact2', f'Привет! я тестовое сообщение от {datetime.datetime.now()}!')
    test_db.save_message('Contact2', 'Client1', f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!')
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.check_user('Client1'))
    print(test_db.check_user('test10'))
    print(test_db.get_history('Contact2'))
    print(test_db.get_history('Contact4'))
    print(test_db.get_history('Contact3'))
    test_db.del_contact('Contact4')
    print(test_db.get_contacts())
