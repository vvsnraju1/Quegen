from helper import *

import unittest


class TestHelper(unittest.TestCase):
    def test_generate_mcq(self):
        data_list = ["Wikipedia is a free online encyclopedia, created and edited by volunteers around the world and "
                     "hosted by the Wikimedia Foundation"]

        result = generate_mcq(data_list)
        expected_result = [
            ['Who hosts Wikipedia?', ['Eff', 'Electronic Frontier Foundation', 'wikimedia foundation', 'United Way'], 'wikimedia foundation', 'Wikipedia is a free online encyclopedia, created and edited by volunteers around the world and hosted by the Wikimedia Foundation'],
            ['What is Wikipedia?', ['Bibliography', 'Wikipedia', 'Scholarly Paper', 'encyclopedia'], 'encyclopedia', 'Wikipedia is a free online encyclopedia, created and edited by volunteers around the world and hosted by the Wikimedia Foundation']
        ]

        self.assertEqual(result, expected_result)

    def test_generate_true_false_questions(self):
        data_list = ["Wikipedia is a free online encyclopedia, created and edited by volunteers around the world and "
                     "hosted by the Wikimedia Foundation"]

        result = generate_true_false_questions(data_list)
        expected_result = [
            ['Is there such a thing as wikipedia?', True, 'Wikipedia is a free online encyclopedia, created and edited by volunteers around the world and hosted by the Wikimedia Foundation']
        ]
        self.assertEqual(result, expected_result)

    def test_clean_sentences(self):
        data_list = ["Wikipedia is a free online encyclopedia", "Hello", "weio wer 4 ;' "]
        result = clean_sentences(data_list)
        expected_result = ['Wikipedia is a free online encyclopedia']
        self.assertEqual(result, expected_result)

    def test_extract_section_names(self):
        data = "1.0 Objective\n some text \n 2:0 Scope\n\n some text \n 2.1 subsection \n some text"
        result = extract_section_names(data)
        expected_result = ['1.0 Objective', '2.0 Scope']
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
