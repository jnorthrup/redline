import re
import uuid


def extract_function_line_numbers(file_path):
    with open(file_path, "r") as file:
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


def extract_function(file_path, function_name, start_line, end_line):
    with open(file_path, "r") as file:
        lines = file.readlines()

    function_code = "".join(lines[start_line - 1 : end_line])
    token = uuid.uuid4().hex[:16]  # 16-byte hexadecimal token
    print(
        f"Function: {function_name}, Line: {start_line} to {end_line}, Token: {token}"
    )
    print(function_code)

    # Write the function with the token to a new file
    with open(f"{function_name}_extracted.py", "w") as out_file:
        out_file.write(f"# Token: {token}\n")
        out_file.write(function_code)

    # Write the token to the function_line_numbers file
    with open("function_line_numbers.txt", "a") as line_numbers_file:
        line_numbers_file.write(f"{function_name}, {start_line}, {end_line}, {token}\n")


if __name__ == "__main__":
    file_path = "redline/supervisor/supervisor.py"
    function_line_numbers = extract_function_line_numbers(file_path)

    for function_name, line_number in function_line_numbers:
        if function_name == "generate":
            extract_function(file_path, function_name, line_number, line_number + 39)
