import unittest
from server import client_message_varification


class TestServer(unittest.TestCase):
    def setUp(self) -> None:
        self.resp_200 = {'response': 200}
        self.resp_400 = {
            'response': 400,
            'error': 'Bad request'
        }

    def test_ok_answer(self):
        self.assertEqual(
            client_message_varification({'action': 'presence', 'time': 12, 'user': {'account_name': 'Guest'}}),
            self.resp_200)

    def test_no_action(self):
        self.assertEqual(client_message_varification({'time': 12, 'user': {'account_name': 'Guest'}}), self.resp_400)

    def test_wrong_action(self):
        self.assertEqual(
            client_message_varification({'action': 'wrong action', 'time': 12, 'user': {'account_name': 'Guest'}}),
            self.resp_400)

    def test_no_time(self):
        self.assertEqual(
            client_message_varification({'action': 'presence', 'user': {'account_name': 'Guest'}}),
            self.resp_400)

    def test_no_user(self):
        self.assertEqual(
            client_message_varification({'action': 'presence', 'time': 12}),
            self.resp_400)

    def test_wrong_name(self):
        self.assertEqual(
            client_message_varification({'action': 'presence', 'time': 12, 'user': {'account_name': 'Vasya'}}),
            self.resp_400)
