from qna_generator import *

import unittest


class TestQnAGenerator(unittest.TestCase):
    def test_mcq_generator(self):
        data_list = ["Wikipedia"]
        result = mcq_generator(data_list)
        expected_result = {'message': 'No MCQ questions generated'}
        self.assertEqual(result, expected_result)

    def test_true_false_generator(self):
        data_list = ["Wikipedia"]
        result = true_false_generator(data_list)
        expected_result = {'message': 'No True/False questions generated'}
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
