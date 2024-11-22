from true_false_generator import *

import unittest


class TestTrueFalseGenerator(unittest.TestCase):
    def test_mcq(self):
        data = {"input_text": "Wikipedia is a free online encyclopedia"}
        result, answer = TrueFalseGen().true_false_questions(payload=data)
        expected_result = {
            'Text': 'Wikipedia is a free online encyclopedia',
            'Count': 4,
            'Boolean Questions': ['Is wikipedia true or false?',
                                  'Is wikipedia a free online encyclopedia?',
                                  'Is wikipedia a free encyclopedia?'
                                  ]
        }

        self.assertEqual(result['Text'], expected_result['Text'])
        self.assertEqual(result['Count'], expected_result['Count'])
        assert result['Boolean Questions'] != 0


if __name__ == '__main__':
    unittest.main()
