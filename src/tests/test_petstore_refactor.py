"""
Tests for petstore refactor.
"""


class TestPetstoreRefactor:
    """
    Test cases for petstore refactor.
    """

    Pet = None  # Define the Pet variable

    def test_case_one(self):
        """
        Test case one.
        """
        # ...existing code...

    def test_case_two(self):
        """
        Test case two.
        """
        # ...existing code...

    def test_case_three(self):
        """
        Test case three.
        """
        # ...existing code...


def fetch(self, item):
    """
    Fetch an item.
    """
    return f"{self.name} fetched {item}!"


class Cat(Pet):
    """
    A class representing a cat.
    """

    def __init__(self, name):
        """
        Initialize a cat with a name.
        """
        super().__init__(name, "cat")

    def scratch(self, item):
        """
        Scratch an item.
        """
        return f"{self.name} scratched {item}!"


def global_function(x):
    """
    Multiply x by 2.
    """
    return x * 2
