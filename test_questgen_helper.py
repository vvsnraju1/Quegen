from questgen_helper import *

import unittest
from sense2vec import Sense2Vec
s2v = Sense2Vec().from_disk('s2v_old')


class TestQuestGenHelper(unittest.TestCase):
    def test_generate_mcq(self):
        result = get_options(answer='Wikipedia', s2v=s2v)
        expected_result = (['Wiki', 'Wiki Article', 'Article', 'First Source', 'Nyt', 'Cites'], 'sense2vec')
        self.assertEqual(result, expected_result)

    def test_mcqs_available(self):
        result = mcqs_available(word='Wikipedia', s2v=s2v)
        expected_result = True
        self.assertEqual(result, expected_result)

    def test_edits(self):
        result = edits(word='Wiki')
        assert len(result) != 0


if __name__ == '__main__':
    unittest.main()
