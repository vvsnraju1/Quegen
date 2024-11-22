from mcq_generator import *

import unittest


class TestMCQGenerator(unittest.TestCase):
    def test_mcq(self):
        data = {"input_text": "Wikipedia is a free online encyclopedia"}
        result = MCQGen().mcq_questions(payload=data)
        expected_result = {
            'statement': 'Wikipedia is a free online encyclopedia', 'questions': [
                {'question_statement': 'What is the free online encyclopedia?',
                 'question_type': 'MCQ',
                 'answer': 'wikipedia', 'id': 1,
                 'options': ['Wiki', 'Article', 'First Source'],
                 'options_algorithm': 'sense2vec', 'extra_options': ['Nyt', 'Cites'],
                 'context': 'Wikipedia is a free online encyclopedia'
                 }
            ],
        }
        self.assertEqual(result['statement'], expected_result['statement'])
        self.assertEqual(result['questions'][0]['question_statement'],
                         expected_result['questions'][0]['question_statement'])
        self.assertEqual(result['questions'][0]['question_type'],
                         expected_result['questions'][0]['question_type'])
        self.assertEqual(result['questions'][0]['context'],
                         expected_result['questions'][0]['context'])


if __name__ == '__main__':
    unittest.main()
