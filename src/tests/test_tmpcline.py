import unittest
from tmpcline import your_function


class TestTmpCline(unittest.TestCase):
    def test_your_function(self):
        input_data = "sample input"
        expected_output = "expected output"
        result = your_function(input_data)
        self.assertEqual(result, expected_output)


if __name__ == "__main__":
    unittest.main()
