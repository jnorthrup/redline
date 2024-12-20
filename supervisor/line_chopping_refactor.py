import os
import re
import uuid
from typing import Any, Dict, List

__all__ = [
    "identify_function_boundaries",
    "extract_functions",
    "generate_unique_ids",
    "add_comment_tokens",
    "refactor_code",
]


def identify_function_boundaries(code: str) -> List[Dict[str, Any]]:
    """
    Identify functions and classes in the given code.

    Args:
        code (str): The code to analyze.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing function/class information
    """
    functions = []
    lines = code.split("\n")
    pattern = re.compile(r"^\s*(def|class)\s+(\w+)[\s\(]")
    import_pattern = re.compile(r"^\s*(import|from)\s+")

    # First collect all imports
    imports = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if import_pattern.match(line):
            imports.append(line)
        elif line.strip() and not import_pattern.match(line):
            # Stop when we hit non-empty, non-import line
            break
        i += 1

    # Now process functions and classes
    functions = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        match = pattern.match(line)
        if match:
            current_indent = len(line) - len(line.lstrip())
            kind, name = match.groups()

            if current_indent == 0:
                start_line = i
                content = [line]
                # Find where this item ends
                next_i = i + 1
                while next_i < len(lines):
                    next_line = lines[next_i].rstrip()
                    if next_line.strip():
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent == 0 and pattern.match(next_line):
                            break
                    next_i += 1

                # Extract content for the current item
                content = lines[start_line:next_i]

                functions.append(
                    {
                        "name": name,
                        "type": kind,
                        "start_line": start_line,
                        "end_line": next_i - 1,
                        "content": content,
                    }
                )
                i = next_i - 1
        i += 1

    for func in functions:
        print(f"Found {func['type']}: {func['name']}")
        print(f"  Start line: {func['start_line']}")
        print(f"  End line: {func['end_line']}")
        print("  Content:")
        for line in func["content"]:
            print(f"    {line}")

    for func in functions:
        print(f"Found {func['type']}: {func['name']}")
        print(f"  Start line: {func['start_line']}")
        print(f"  End line: {func['end_line']}")
        print("  Content:")
        for line in func["content"]:
            print(f"    {line}")

    return functions


def generate_unique_ids(functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate unique IDs for each function/class.

    Args:
        functions (List[Dict[str, Any]]): List of function/class dictionaries

    Returns:
        List[Dict[str, Any]]: Functions with added unique IDs
    """
    used_ids = set()
    for func in functions:
        while True:
            new_id = str(uuid.uuid4())
            if new_id not in used_ids:
                func["id"] = new_id
                used_ids.add(new_id)
                break
    return functions


def add_comment_tokens(code: str, functions: List[Dict[str, Any]]) -> str:
    """
    Add comment tokens to mark function boundaries.

    Args:
        code (str): Original code
        functions (List[Dict[str, Any]]): List of functions with IDs

    Returns:
        str: Code with added comment tokens
    """
    lines = code.split("\n")
    output_lines = []

    for i, line in enumerate(lines):
        for func in functions:
            if i == func["start_line"]:
                output_lines.append(f"# FUNCTION_ID: {func['id']}")
        output_lines.append(line)
        for func in functions:
            if i == func["end_line"]:
                output_lines.append(f"# END_FUNCTION_ID: {func['id']}")

    return "\n".join(output_lines)


def extract_functions(code: str, functions: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Extract functions into separate code blocks.

    Args:
        code (str): Original code
        functions (List[Dict[str, Any]]): List of functions to extract

    Returns:
        Dict[str, str]: Dictionary mapping function names to their code
    """
    extracted = {}
    for func in functions:
        lines = func["content"]

        # Get the base indentation level from the first line
        base_indent = len(lines[0]) - len(lines[0].lstrip())

        # Process each line
        formatted_lines = []
        for i, line in enumerate(lines):
            if not line.strip():  # Empty line
                formatted_lines.append("")
                continue

            current_indent = len(line) - len(line.lstrip())
            if i == 0:  # First line (function/class definition)
                formatted_lines.append(line.lstrip())
            else:
                # For functions, remove all indentation
                # For classes, keep relative indentation for methods
                if func["type"] == "class":
                    relative_indent = current_indent - base_indent
                    if relative_indent > 0:
                        formatted_lines.append(
                            "    " * (relative_indent // 4) + line.lstrip()
                        )
                    else:
                        formatted_lines.append(line.lstrip())
                else:
                    formatted_lines.append(line[base_indent:])

        content = "\n".join(formatted_lines)

        # Add pass statement if body is empty
        if len(formatted_lines) == 1 or not any(
            line.strip() for line in formatted_lines[1:]
        ):
            indent = "    " if func["type"] == "class" else ""
            formatted_lines.append(f"{indent}pass")
            content = "\n".join(formatted_lines)

        extracted[func["name"]] = content
    return extracted


def _verify_chopping(code: str, functions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify the integrity of the chopping process by collecting metrics.
    """
    metrics = {}
    metrics["original_line_count"] = len(code.split("\n"))
    metrics["function_count"] = len(functions)
    return metrics


def refactor_code(filename: str, delegate=None, verify=False, filters=None) -> None:
    """
    Refactor code by extracting functions into separate files.
    Optionally uses a delegate to manage type system echoes.
    """
    with open(filename, "r") as f:
        code = f.read()

    # Identify functions and classes
    functions = identify_function_boundaries(code)
    functions = generate_unique_ids(functions)

    # If a delegate is provided, call it to handle type hints or signatures
    if delegate:
        for func in functions:
            delegate.handle_type_info(func)

    # Verification step
    if verify:
        chop_metrics = _verify_chopping(code, functions)
        print(f"Verification metrics: {chop_metrics}")
        # Example filter usage (minimal demonstration)
        if filters and "min_functions" in filters:
            if chop_metrics["function_count"] < filters["min_functions"]:
                print("Warning: function count below expected threshold")

    # Extract each function/class to its own file
    extracted = extract_functions(code, functions)

    # Write each function/class to a separate file
    for name, content in extracted.items():
        output_filename = f"{name}.py"
        with open(output_filename, "w") as f:
            f.write(content)


class DefaultDelegate:
    """
    Example delegate to illustrate type echo management.
    """

    def handle_type_info(self, func):
        # Minimal example: print the function name for demonstration
        # In a real implementation, adjust or validate type hints as needed
        print(f"Delegate is handling type info for {func['name']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Refactor Python code by extracting functions and classes."
    )
    parser.add_argument("filename", help="Python file to refactor")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Enable verification metrics after chopping",
    )
    parser.add_argument(
        "--min_functions", type=int, help="Specify minimum number of functions expected"
    )
    args = parser.parse_args()

    filters = {}
    if args.min_functions:
        filters["min_functions"] = args.min_functions

    refactor_code(args.filename, verify=args.verify, filters=filters)
