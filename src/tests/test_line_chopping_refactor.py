import unittest

from redline.extract_functions import extract_functions


class TestLineChoppingRefactor(unittest.TestCase):

    def test_extract_functions_basic(self):
        code = """
        def foo():
            print("hello")
        def bar():
            print("world")
        """
        expected = [
            ("foo", 'def foo():\n            print("hello")'),
            ("bar", 'def bar():\n            print("world")'),
        ]
        actual = extract_functions(code)
        self.assertEqual(actual, expected)

    def test_extract_functions_with_comments(self):
        code = """
        # this is a comment
        def foo():
            print("hello") # inline comment
        def bar():
            '''
            this is a docstring
            '''
            print("world")
        """
        expected = [
            ("foo", 'def foo():\n            print("hello") # inline comment'),
            (
                "bar",
                "def bar():\n            '''\n            this is a docstring\n            '''\n            print(\"world\")",
            ),
        ]
        actual = extract_functions(code)
        self.assertEqual(actual, expected)

    def test_extract_functions_with_class(self):
        code = """
        class MyClass:
            def __init__(self):
                pass
            def foo(self):
                print("hello")
        def bar():
            print("world")
        """
        expected = [
            ("__init__", "def __init__(self):\n                pass"),
            ("foo", 'def foo(self):\n                print("hello")'),
            ("bar", 'def bar():\n            print("world")'),
        ]
        actual = extract_functions(code)
        self.assertEqual(actual, expected)

    def test_extract_functions_no_functions(self):
        code = """
        # this is a comment
        x = 1
        y = 2
        """
        expected = []
        actual = extract_functions(code)
        self.assertEqual(actual, expected)

    def test_extract_functions_nested_functions(self):
        code = """
        def foo():
            def bar():
                print("hello")
            print("world")
        """
        expected = [
            (
                "foo",
                'def foo():\n            def bar():\n                print("hello")\n            print("world")',
            ),
        ]
        actual = extract_functions(code)
        self.assertEqual(actual, expected)

    def test_extract_functions_multiline_def(self):
        code = """
        def foo(
            a,
            b
        ):
            print("hello")
        """
        expected = [
            (
                "foo",
                'def foo(\n            a,\n            b\n        ):\n            print("hello")',
            ),
        ]
        actual = extract_functions(code)
        self.assertEqual(actual, expected)
