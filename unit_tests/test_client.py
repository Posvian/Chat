import unittest
from client import server_answer_parser, make_presence


class TestClient(unittest.TestCase):
    def setUp(self) -> None:
        self.test = make_presence()
        self.test['time'] = 12

    def test_ok_answer(self):
        self.assertEqual(server_answer_parser({'response': 200}), '200 : OK')

    def test_400_answer(self):
        self.assertEqual(server_answer_parser({'response': 400, 'error': 'Bad request'}), '400 : Bad request')

    def test_400_answer_2(self):
        self.assertRaises(ValueError, server_answer_parser, {'400': 'Bad request'})

    def test_make_presence(self):
        self.assertEqual(self.test, {'action': 'presence', 'time': 12,'user': {'account_name': 'Guest'}})


