import unittest
from pgpcr import fmt

class Fmt(unittest.TestCase):
    def setUp(self):
        self.data = "tests/data"

    def test_backups(self):
        b = fmt.backups(self.data)
        self.assertEqual(b, ["B000DEAD", "CAFEBABE", "DEADBEEF"])

