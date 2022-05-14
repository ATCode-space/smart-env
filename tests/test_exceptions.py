import unittest

from smart_env.exceptions import UnsupportedAction


class ExceptionTestCase(unittest.TestCase):
    def test_001_representation_of_unsupported_action(self):
        action = 'Unsupported Action'
        cmp_representation = 'Unsupported action: {}'.format(action)
        self.assertEqual(str(UnsupportedAction(action)), cmp_representation)

    def test_002_representation_of_unsupported_undefined_action(self):
        self.assertEqual(str(UnsupportedAction()), 'This action is not supported')
