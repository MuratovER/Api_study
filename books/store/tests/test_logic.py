from unittest import TestCase

from store.logic import operations


class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(6, 13, '+')
        self.assertEqual(19, result)

    def test_minus(self):
        result = operations(13, 5, '-')
        self.assertEqual(8, result)

    def test_multiply(self):
        result = operations(3, 6, '*')
        self.assertEqual(18, result)
        