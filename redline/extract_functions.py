"""Module for extracting functions from Python source files."""

import re
import uuid


def extract_function_line_numbers(file_path):
    """
    Extract function definitions from a Python file and their line numbers.
    
    Args:
        file_path (str): Path to Python source file
    
    Returns:
        list: List of tuples containing function names and their line numbers
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    function_pattern = re.compile(r"^\s*def\s+(\w+)\s*\(")
    function_line_numbers = []

    for i, line in enumerate(lines, start=1):
        match = function_pattern.match(line)
        if match:
            function_name = match.group(1)
            function_line_numbers.append((function_name, i))

    for function_name, line_number in function_line_numbers:
        print(f"Function: {function_name}, Line: {line_number}")

    return function_line_numbers


def extract_function(file_path, function_name):
    """Extract function from file."""
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    function_code = "".join(lines[start_line - 1 : end_line])
    token = uuid.uuid4().hex[:16]  # 16-byte hexadecimal token
    print(
        f"Function: {function_name}, Line: {start_line} to {end_line}, Token: {token}"
    )
    print(function_code)

    write_function(f"{function_name}_extracted.py", function_name, function_code)

    # Write the token to the function_line_numbers file
    with open("function_line_numbers.txt", "a", encoding="utf-8") as line_numbers_file:
        line_numbers_file.write(f"{function_name}, {start_line}, {end_line}, {token}\n")


def write_function(file_path, function_name, content):
    """
    Write extracted function to a new file.
    
    Args:
        file_path (str): Output file path
        function_name (str): Name of the function
        content (str): Function code
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"# Token: {uuid.uuid4().hex[:16]}\n")
        file.write(content)


def extract_functions(file_path: str) -> None:
    function_line_numbers = extract_function_line_numbers(file_path)
    for function_name, line_number in function_line_numbers:
        if function_name == "generate":
            extract_function(file_path, function_name, line_number, line_number + 39)


if __name__ == "__main__":
    FILE_PATH = "redline/supervisor/supervisor.py"  # Conform to UPPER_CASE naming style
    extract_functions(FILE_PATH)
