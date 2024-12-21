"""
This module provides functionality for refactoring code by line chopping,
including identifying function boundaries, extracting functions,
generating unique IDs, and applying DSL-based transformations.
"""

import os
import re
import uuid
import subprocess
import argparse
import sys
from typing import Any, Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

__all__ = [
    "identify_function_boundaries",
    "extract_functions",
    "generate_unique_ids",
    "add_comment_tokens",
    "refactor_code",
    "get_file_flavor",
    "register_visitor_plugin",
    "execute_visitor_plugins",
    "parse_arguments",
    "verify_refactoring",
    "parse_dsl",
    "scan_code",
    "migrate_manual_steps_to_dsl",
    "integrate_custom_actions_into_dsl",
    "extract_and_refactor_lines",
    "rename_entity",
    "indent_code",
    "example_script",
    "run_unit_tests",
    "process_file",
    "main",
    "extract_lines",
    "rename_entity_primitive",
    "handle_dsl_command",
]

# Constants for DSL commands and patterns
DSL_COMMANDS = {
    "SCAN": {
        "classes": lambda code, flavor, params: scan_classes(code, flavor, params),
    },
    "FIND": {
        "duplicates": lambda results, params: find_duplicates(results, params)
    }
}

# REGEX patterns in REGEX_GREP_MAP
REGEX_GREP_MAP = {
    "python": {
        "function": r"def\s+(\w+)\s*\(",  # Identifies Python function declarations
        "class": r"class\s+(\w+)\s*\(",  # Identifies Python class declarations
    },
    "typescript": {
        "function": r"function\s+(\w+)\s*\(",  # Identifies TypeScript function declarations
        "class": r"class\s+(\w+)\s*\{",  # Identifies TypeScript class declarations
    },
    "javascript": {
        "function": r"function\s+(\w+)\s*\(",  # Identifies JavaScript function declarations
        "class": r"class\s+(\w+)\s*\{",  # Identifies JavaScript class declarations
    },
    # ...additional file flavors...
}


def get_file_flavor(file_extension: str) -> str:
    """
    Get the file flavor based on the file extension.

    Args:
        file_extension (str): The file extension.

    Returns:
        str: The file flavor.
    """
    logging.debug("Entering get_file_flavor")
    logging.debug("Entering get_file_flavor with file_extension: %s", file_extension)
    file_flavors = {
        ".py": "python",
        ".ts": "typescript",
        ".js": "javascript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".cs": "csharp",
        ".rb": "ruby",
        ".go": "go",
        ".rs": "rust",
        ".php": "php",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".xml": "xml",
        ".yaml": "yaml",
        ".yml": "yaml",
    }
    result = file_flavors.get(file_extension, "unknown")
    logging.debug("Exiting get_file_flavor with result: %s", result)
    return result


# Regex patterns in identify_function_boundaries function
def identify_function_boundaries(code: str, flavor: str) -> List[Dict[str, Any]]:
    """
    Identify functions and classes in the given code.

    Args:
        code (str): The code to analyze.
        flavor (str): The file flavor (e.g., python, typescript).

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing function/class information
    """
    logging.debug("Entering identify_function_boundaries")
    boundaries = []
    for i, line in enumerate(code.splitlines()):
        if flavor == "python" and re.match(r"(class|def) ", line):
            boundaries.append({"line_number": i, "line": line})
        elif flavor == "typescript" and re.match(r"(class|function) ", line):
            boundaries.append({"line_number": i, "line": line})
    logging.debug("Found boundaries: %s", boundaries)
    logging.debug("Exiting identify_function_boundaries")
    return boundaries


def generate_unique_ids(code: str, flavor: str) -> str:
    """
    Generate unique IDs for functions and classes in the given code.

    Args:
        code (str): The code to analyze.
        flavor (str): The file flavor (e.g., python, typescript).

    Returns:
        str: The code with unique IDs added.
    """
    logging.debug("Entering generate_unique_ids")
    lines = code.splitlines()
    boundaries = identify_function_boundaries(code, flavor)
    for boundary in boundaries:
        unique_id = str(uuid.uuid4())
        lines.insert(boundary["line_number"], f"# {unique_id}")
    logging.debug("Unique IDs generated")
    logging.debug("Exiting generate_unique_ids")
    return "\n".join(lines)


def add_comment_tokens(code: str, flavor: str) -> str:
    """
    Add comment tokens to the given code.

    Args:
        code (str): The code to analyze.
        flavor (str): The file flavor (e.g., python, typescript).

    Returns:
        str: The code with comment tokens added.
    """
    logging.debug("Entering add_comment_tokens")
    # This function is now redundant, as generate_unique_ids adds the comment tokens
    logging.debug("add_comment_tokens is now redundant")
    logging.debug("Exiting add_comment_tokens")
    return code


def extract_functions(code: str, flavor: str) -> List[str]:
    """
    Extract functions from the given code.

    Args:
        code (str): The code to analyze.
        flavor (str): The file flavor (e.g., python, typescript).

    Returns:
        List[str]: List of extracted functions.
    """
    logging.debug("Entering extract_functions")
    functions = []
    boundaries = identify_function_boundaries(code, flavor)
    lines = code.splitlines()
    prev_line = 0
    for boundary in boundaries:
        start_line = boundary["line_number"]
        if prev_line != 0:
            function_code = lines[prev_line:start_line]
        else:
            function_code = lines[:start_line]
        functions.append("\n".join(function_code))
        prev_line = start_line
    if prev_line != 0:
        function_code = lines[prev_line:]
        functions.append("\n".join(function_code))
    logging.debug("Extracted %s functions", len(functions))
    logging.debug("Exiting extract_functions")
    return functions


# Regex patterns in refactor_code function
def refactor_code(code: str, file_path: str, flavor: str) -> str:
    """
    Refactor the given code.

    Args:
        code (str): The code to analyze.
        file_path (str): The path to the file.
        flavor (str): The file flavor (e.g., python, typescript).

    Returns:
        str: The refactored code.
    """
    logging.debug("Entering refactor_code")
    output_dir = "agent_functions"
    os.makedirs(output_dir, exist_ok=True)

    lines = code.splitlines()
    boundaries = identify_function_boundaries(code, flavor)
    prev_line = 0
    modified_lines = []
    for boundary in boundaries:
        start_line = boundary["line_number"]
        if prev_line != 0:
            function_code = lines[prev_line:start_line]
            modified_lines.extend(lines[prev_line:start_line])
        else:
            function_code = lines[:start_line]
            modified_lines.extend(lines[:start_line])

        unique_id = str(uuid.uuid4())
        match = re.search(r"(class|def|function) (\w+)", lines[start_line])
        function_name = match.group(2) if match else "unknown"
        output_file = os.path.join(
            output_dir, f"{function_name}{os.path.splitext(file_path)[1]}"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(function_code))

        with open(output_file, "r+", encoding="utf-8") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(f"# {unique_id}\n{content}")

        modified_lines.insert(start_line, f"# {unique_id}")
        modified_lines.insert(start_line, lines[start_line])
        if flavor == "python":
            if start_line + 1 < len(lines):
                modified_lines.insert(
                    start_line + 2,
                    re.sub(
                        r"def (\w+)\(self\)",
                        r"def \1(self, obj)",
                        lines[start_line + 1],
                    ),
                )
            else:
                logging.warning("Skipping parameter renaming due to index out of range")
        prev_line = start_line + 1

    if prev_line != 0:
        function_code = lines[prev_line:]
        modified_lines.extend(lines[prev_line:])
        match = re.search(r"(class|def|function) (\w+)", lines[prev_line])
        function_name = match.group(2) if match else "unknown"
        output_file = os.path.join(
            output_dir, f"{function_name}{os.path.splitext(file_path)[1]}"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(function_code))

        with open(output_file, "r+", encoding="utf-8") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(f"# {uuid.uuid4()}\n{content}")

        modified_lines.insert(prev_line, f"# {uuid.uuid4()}")
        modified_lines.insert(prev_line + 1, lines[prev_line])
        if flavor == "python":
            if prev_line + 1 < len(lines):
                modified_lines.insert(
                    prev_line + 2,
                    re.sub(
                        r"def (\w+)\(self\)", r"def \1(self, obj)", lines[prev_line + 1]
                    ),
                )
            else:
                logging.warning("Skipping parameter renaming due to index out of range")

    modified_code = "\n".join(modified_lines)

    lint_files = [file_path] + [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(os.path.splitext(file_path)[1])
    ]
    for file in lint_files:
        try:
            subprocess.run(["black", file], check=True)
        except subprocess.CalledProcessError as e:
            logging.debug("Error linting file %s: %s", file, e)

    logging.debug("Refactoring completed")
    logging.debug("Exiting refactor_code")
    return modified_code


def parse_arguments():
    """Parse command line arguments."""
    logging.debug("Entering parse_arguments")
    logging.debug("Parsing arguments")
    parser = argparse.ArgumentParser(
        description="Line Chopping Refactoring Tool - Analyzes and refactors code with support for class scanning and duplicate detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Scan for duplicate classes:
    %(prog)s src --scan_only --dsl "SCAN classes -> case=insensitive; FIND duplicates -> report"
  
  Verify refactoring:
    %(prog)s src/file.py --verify --min_functions 5
  
  Generate diagram:
    %(prog)s src/file.py --render_mermaid

DSL Commands:
  SCAN classes -> case=sensitive|insensitive
  FIND duplicates -> report
  CHOP lines 10-20
  CHOP def function_name rename=new_name
  CHOP class ClassName rename=NewName
""")

    parser.add_argument("path", 
                       help="Path to input file or directory to analyze/refactor")
    
    parser.add_argument("--verify", 
                       action="store_true",
                       help="Enable verification metrics for refactoring results")
    
    parser.add_argument("--min_functions", 
                       type=int, 
                       default=1,
                       help="Specify minimum number of functions required after refactoring")
    
    parser.add_argument("--scan_only", 
                       action="store_true",
                       help="Perform analysis without modifying files (used with --dsl)")
    
    parser.add_argument("--dsl", 
                       type=str,
                       help="DSL instructions for scanning/refactoring (see Examples section)")
    
    parser.add_argument("--run_example", 
                       action="store_true",
                       help="Run example script demonstrating tool usage")
    
    parser.add_argument("--run_tests", 
                       action="store_true",
                       help="Run unit tests to verify tool functionality")
    
    parser.add_argument("--render_mermaid", 
                       action="store_true",
                       help="Generate Mermaid diagram visualization of code structure")
    
    parser.add_argument("--propose", 
                       action="store_true",
                       help="Show proposed refactoring changes without applying them")

    logging.debug("Exiting parse_arguments")
    return parser.parse_args()


def verify_refactoring(
    output_dir: str, original_function_count: int, new_function_count: int
):
    """
    Verify the refactoring process.

    Args:
        output_dir (str): The output directory.
        original_function_count (int): The original number of functions.
        new_function_count (int): The new number of functions.
    """
    logging.debug("Entering verify_refactoring")
    logging.debug("Verifying refactoring")
    if new_function_count < original_function_count:
        print(
            f"Warning: Expected at least {original_function_count} functions, found {new_function_count}"
        )
    else:
        print("Verification passed: Function count meets the requirement.")
    logging.debug("Exiting verify_refactoring")


def parse_dsl(dsl_instructions: str) -> List[Dict[str, Any]]:
    """Parse DSL instructions with enhanced class scanning support."""
    logging.debug("Parsing DSL instructions: %s", dsl_instructions)
    
    instructions = []
    for instruction in dsl_instructions.split(";"):
        instruction = instruction.strip()
        if not instruction:
            continue
            
        parts = instruction.split("->")
        if len(parts) != 2:
            logging.warning("Invalid DSL instruction: %s", instruction)
            continue
            
        command_parts = parts[0].strip().split()
        action = command_parts[0].upper()
        target = command_parts[1] if len(command_parts) > 1 else ""
        params = parts[1].strip()
        
        instructions.append({
            "action": action,
            "target": target,
            "params": params
        })
    
    return instructions


def scan_code(code: str, flavor: str) -> List[Dict[str, Any]]:
    """
    Scan code for API definitions.

    Args:
        code (str): The code to scan.
        flavor (str): The file flavor.

    Returns:
        List[Dict[str, Any]]: List of API definitions.
    """
    logging.debug("Entering scan_code")
    logging.debug("Scanning code for API")
    boundaries = identify_function_boundaries(code, flavor)
    api_scan = [
        {
            "type": boundary["line"].split()[0],
            "name": re.search(r"(class|def|function) (\w+)", boundary["line"]).group(2),
        }
        for boundary in boundaries
    ]
    logging.debug("Exiting scan_code")
    return api_scan


def migrate_manual_steps_to_dsl(
    instructions: List[Dict[str, Any]], code: str, flavor: str
) -> str:
    """
    Migrate manual refactoring steps to DSL-driven commands.

    Args:
        instructions (List[Dict[str, Any]]): Parsed DSL instructions.
        code (str): The original code to refactor.
        flavor (str): The file flavor (e.g., python, typescript).

    Returns:
        str: The refactored code.
    """
    logging.debug("Entering migrate_manual_steps_to_dsl")
    for instruction in instructions:
        code = handle_dsl_command(instruction, code, flavor)
    logging.debug("Exiting migrate_manual_steps_to_dsl")
    return code


def integrate_custom_actions_into_dsl(
    instructions: List[Dict[str, Any]], code: str, flavor: str
) -> str:
    """
    Integrate custom refactoring actions into the DSL framework.

    Args:
        instructions (List[Dict[str, Any]]): Parsed DSL instructions.
        code (str): The code to refactor.
        flavor (str): The file flavor (e.g., python, typescript).

    Returns:
        str: The refactored code after custom actions.
    """
    logging.debug("Entering integrate_custom_actions_into_dsl")
    for instruction in instructions:
        action = instruction.get("action")
        params = instruction.get("params")
        if action.startswith("CHOP def") or action.startswith("CHOP class"):
            rename_match = re.search(
                r"rename=(\w+)", params
            )  # Matches rename parameters
            if rename_match:
                new_name = rename_match.group(1)
                code = rename_entity(code, action, new_name, flavor)
                logging.debug("Renamed entity to %s", new_name)
        # Handle additional custom actions as needed
    logging.debug("Exiting integrate_custom_actions_into_dsl")
    return code


def extract_and_refactor_lines(code: str, start: int, end: int, flavor: str) -> str:
    """
    Extract lines from start to end and refactor them into a new function or class.

    Args:
        code (str): The original code.
        start (int): Starting line number.
        end (int): Ending line number.
        flavor (str): The file flavor.

    Returns:
        str: The refactored code.
    """
    logging.debug("Entering extract_and_refactor_lines")
    lines = code.splitlines()
    extracted_code = "\n".join(lines[start - 1 : end])
    unique_id = str(uuid.uuid4())
    new_function_name = f"extracted_function_{unique_id.replace('-', '')[:8]}"
    refactored_code = (
        f"# {unique_id}\n"
        f"def {new_function_name}():\n"
        f"{indent_code(extracted_code, 4)}\n"
    )
    lines[start - 1 : end] = [refactored_code]
    logging.debug("Extracted lines %s-%s into %s", start, end, new_function_name)
    logging.debug("Exiting extract_and_refactor_lines")
    return "\n".join(lines)


def rename_entity(code: str, action: str, new_name: str, flavor: str) -> str:
    """
    Rename a function or class based on the DSL command.

    Args:
        code (str): The original code.
        action (str): The action string from DSL.
        new_name (str): The new name for the entity.
        flavor (str): The file flavor.

    Returns:
        str: The code with the renamed entity.
    """
    logging.debug("Entering rename_entity")
    match = re.search(
        r"(def|class) (\w+)", action
    )  # Captures entity type and old name for renaming
    if match:
        entity_type, old_name = match.groups()
        code = re.sub(
            rf"\b{entity_type} {old_name}\b", f"{entity_type} {new_name}", code
        )  # Renames the entity
        logging.debug("Renamed %s from %s to %s", entity_type, old_name, new_name)
    logging.debug("Exiting rename_entity")
    return code


def indent_code(code: str, spaces: int) -> str:
    """
    Indent code by a specified number of spaces.

    Args:
        code (str): The code to indent.
        spaces (int): Number of spaces for indentation.

    Returns:
        str: Indented code.
    """
    indentation = " " * spaces
    return "\n".join(
        indentation + line if line.strip() != "" else line for line in code.splitlines()
    )


def example_script():
    """
    Demonstrates the line chopping refactoring process.
    """
    logging.debug("Entering example_script")
    import os
    import re
    import uuid
    import subprocess

    # Define the input file and output directory
    input_file = "supervisor.py"
    output_dir = "agent_functions"

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Identify function boundaries and object features
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    boundaries = []
    for i, line in enumerate(lines):
        if re.match(r"(class|def) ", line):
            boundaries.append(i)

    # Step 2: Extract and write functions
    prev_line = 0
    for start_line in boundaries:
        # Extract the function
        if prev_line != 0:
            function_code = lines[prev_line:start_line]
        else:
            function_code = lines[:start_line]

        # Generate a unique ID
        unique_id = str(uuid.uuid4())

        # Write the function to a new file
        function_name = re.search(r"(class|def) (\w+)", lines[start_line]).group(2)
        output_file = os.path.join(output_dir, f"{function_name}.py")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("".join(function_code))

        # Add unique comment token
        with open(output_file, "r+", encoding="utf-8") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(f"# {unique_id}\n{content}")

        # Add unique comment token to the original file
        lines.insert(start_line, f"# {unique_id}\n")

        # Update the original class to accept the object prototype
        if start_line + 1 < len(lines):
            lines[start_line + 1] = re.sub(
                r"def (\w+)\(self\)", r"def \1(self, obj)", lines[start_line + 1]
            )

        prev_line = start_line + 1

    # Handle the last function
    if prev_line != 0:
        function_code = lines[prev_line:]
        function_name = re.search(r"(class|def) (\w+)", lines[prev_line]).group(2)
        output_file = os.path.join(output_dir, f"{function_name}.py")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("".join(function_code))

        # Add unique comment token
        with open(output_file, "r+", encoding="utf-8") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(f"# {uuid.uuid4()}\n{content}")

        # Add unique comment token to the original file
        lines.insert(prev_line, f"# {uuid.uuid4()}\n")

        # Update the original class to accept the object prototype
        if prev_line + 1 < len(lines):
            lines[prev_line + 1] = re.sub(
                r"def (\w+)\(self\)", r"def \1(self, obj)", lines[prev_line + 1]
            )

    # Debug: Print the modified lines
    print("Modified lines:")
    print("".join(lines))

    # Write the modified lines back to the original file
    with open(input_file, "w", encoding="utf-8") as file:
        file.writelines(lines)

    # Step 3: Lint the resulting files
    lint_files = [input_file] + [
        os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".py")
    ]
    for file in lint_files:
        subprocess.run(["black", file])

    print("Line chopping refactoring completed successfully.")
    logging.debug("Exiting example_script")


# Added Unit Tests
def run_unit_tests():
    """
    Runs unit tests for the line chopping refactoring tool.
    """
    logging.debug("Entering run_unit_tests")
    import unittest

    class TestLineChoppingRefactoring(unittest.TestCase):
        """
        Unit tests for the line chopping refactoring tool.
        """

        def setUp(self):
            self.input_file = "test_supervisor.py"
            self.output_dir = "test_agent_functions"
            self.sample_code = """
class Supervisor:
    def __init__(self):
        pass

    def manage(self):
        print("Managing")

    def report(self):
        print("Reporting")
"""
            with open(self.input_file, "w", encoding="utf-8") as f:
                f.write(self.sample_code)
            os.makedirs(self.output_dir, exist_ok=True)

        def tearDown(self):
            os.remove(self.input_file)
            for file in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, file))
            os.rmdir(self.output_dir)

        def test_identify_function_boundaries(self):
            with open(self.input_file, "r", encoding="utf-8") as file:
                code = file.read()
            boundaries = identify_function_boundaries(code, "python")
            expected = [
                {"line_number": 1, "line": "class Supervisor:\\n"},
                {"line_number": 4, "line": "    def manage(self):\\n"},
                {"line_number": 7, "line": "    def report(self):\\n"},
            ]
            self.assertEqual(boundaries, expected)

        def test_generate_unique_ids(self):
            with open(self.input_file, "r", encoding="utf-8") as file:
                code = file.read()
            refactored_code = generate_unique_ids(code, "python")
            unique_ids = re.findall(r"# ([a-f0-9\-]{36})", refactored_code)
            self.assertEqual(len(unique_ids), 3)

    # Create and run test suite with all test methods
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLineChoppingRefactoring)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
    logging.debug("Exiting run_unit_tests")




# Visitor Plugin Framework

visitor_plugins = []


def register_visitor_plugin(plugin):
    """
    Register a visitor plugin.

    Args:
        plugin (function): The plugin function to register.
    """
    visitor_plugins.append(plugin)


def execute_visitor_plugins(code: str, flavor: str):
    """
    Execute all registered visitor plugins.

    Args:
        code (str): The code to process.
        flavor (str): The file flavor.
    """
    for plugin in visitor_plugins:
        plugin(code, flavor)


# Example visitor plugin: Mermaid model renderer
def mermaid_model_renderer(code: str, flavor: str):
    """
    Renders a mermaid diagram of the code.
    """
    api_scan = scan_code(code, flavor)
    mermaid_diagram = render_mermaid_diagram(api_scan)
    print("Mermaid Diagram:")
    print(mermaid_diagram)


# Register the Mermaid model renderer plugin
register_visitor_plugin(mermaid_model_renderer)

# ...existing code...


def extract_lines(code: str, start: int, end: int, flavor: str) -> str:
    """
    Extract lines from start to end into a new function or class.

    Args:
        code (str): The original code.
        start (int): Starting line number.
        end (int): Ending line number.
        flavor (str): The file flavor.

    Returns:
        str: The refactored code with extracted lines.
    """
    logging.debug("Entering extract_lines")
    result = extract_and_refactor_lines(code, start, end, flavor)
    logging.debug("Exiting extract_lines")
    return result


def rename_entity_primitive(
    code: str, entity_type: str, old_name: str, new_name: str, flavor: str
) -> str:
    """
    Rename a function or class based on the provided entity type and names.

    Args:
        code (str): The original code.
        entity_type (str): Type of the entity ('def' or 'class').
        old_name (str): Current name of the entity.
        new_name (str): New name for the entity.
        flavor (str): The file flavor.

    Returns:
        str: The code with the renamed entity.
    """
    logging.debug("Entering rename_entity_primitive")
    result = rename_entity(code, f"{entity_type} {old_name}", new_name, flavor)
    logging.debug("Exiting rename_entity_primitive")
    return result


def scan_classes(code: str, flavor: str, params: str, file_path: str = "") -> List[Dict[str, Any]]:
    """Scan code specifically for class definitions."""
    logging.debug("Scanning for classes in %s with params: %s", file_path, params)
    
    case_sensitive = "case=insensitive" not in params
    pattern = REGEX_GREP_MAP[flavor]["class"]
    
    classes = []
    for i, line in enumerate(code.splitlines()):
        match = re.search(pattern, line)
        if match:
            class_name = match.group(1)
            classes.append({
                "type": "class",
                "name": class_name,
                "line": i + 1,
                "file": file_path,
                "original_case": class_name,
                "compare_case": class_name if case_sensitive else class_name.lower()
            })
    
    return classes

def find_duplicates(scan_results: List[Dict[str, Any]], params: str) -> List[Dict[str, Any]]:
    """Find duplicate classes in scan results."""
    logging.debug("Finding duplicates in %d scanned classes", len(scan_results))
    
    from collections import defaultdict
    class_map = defaultdict(list)
    
    # Group by case-insensitive name
    for result in scan_results:
        class_map[result["compare_case"]].append(result)
    
    # Filter and format duplicates
    duplicates = []
    for name, instances in class_map.items():
        if len(instances) > 1:
            duplicates.append({
                "name": name,
                "count": len(instances),
                "instances": [{
                    "file": inst["file"],
                    "line": inst["line"],
                    "original_name": inst["original_case"]
                } for inst in instances]
            })
    
    return duplicates

def handle_dsl_command(command: Dict[str, Any], code: str, flavor: str) -> Any:
    """Handle DSL commands including class scanning."""
    logging.debug("Handling DSL command: %s", command)
    
    action = command["action"]
    target = command["target"]
    params = command["params"]
    
    if action == "SCAN":
        if target in DSL_COMMANDS["SCAN"]:
            return DSL_COMMANDS["SCAN"][target](code, flavor, params)
            
    elif action == "FIND":
        if target in DSL_COMMANDS["FIND"]:
            return DSL_COMMANDS["FIND"][target](code, params)
    elif action.startswith("CHOP"):
        if "lines" in target:
            lines_range = re.findall(r"\d+", target)
            if len(lines_range) == 2:
                start, end = map(int, lines_range)
                return extract_lines(code, start, end, flavor)
        elif target.startswith("def ") or target.startswith("class "):
            entity_type, name = target.split()
            new_name = params.split("=")[1] if "=" in params else name
            return rename_entity_primitive(code, entity_type, name, new_name, flavor)
    
    logging.warning("Unknown command: %s %s", action, target)
    return None

def process_file(file_path: str, args: argparse.Namespace) -> List[Dict[str, Any]]:
    """Process the file based on the provided arguments."""
    logging.debug("Processing file: %s", file_path)
    
    flavor = get_file_flavor(os.path.splitext(file_path)[1])
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()
    except (UnicodeDecodeError, IOError) as e:
        logging.warning(f"Skipping {file_path}: {str(e)}")
        return []

    if args.scan_only:
        if args.dsl:
            instructions = parse_dsl(args.dsl)
            results = None
            for instruction in instructions:
                if instruction["action"] == "SCAN" and instruction["target"] == "classes":
                    # Pass file path to scan_classes for better reporting
                    results = scan_classes(code, flavor, instruction["params"], file_path)
                elif results is not None:
                    results = handle_dsl_command(instruction, results, flavor)
            return results or []
        else:
            api_scan = scan_code(code, flavor)
            if args.render_mermaid:
                mermaid_diagram = render_mermaid_diagram(api_scan)
                print("Mermaid Diagram:")
                print(mermaid_diagram)
            return api_scan

    if args.dsl:
        instructions = parse_dsl(args.dsl)
        results = None
        
        for instruction in instructions:
            if results is None:
                results = handle_dsl_command(instruction, code, flavor)
            else:
                results = handle_dsl_command(instruction, results, flavor)
        
        if results and isinstance(results, list):
            if any(isinstance(r, dict) and "duplicates" in r for r in results):
                print("\nDuplicate Classes Found:")
                for r in results:
                    if "duplicates" in r:
                        for dup in r["duplicates"]:
                            print(f"\nClass name: {dup['name']}")
                            for inst in dup["instances"]:
                                print(f"  Found in {file_path}:{inst['line']}")
            return
        elif results:
            code = results

    execute_visitor_plugins(code, flavor)  # Execute visitors before refactoring

    refactored_code = refactor_code(code, file_path, flavor)

    execute_visitor_plugins(
        refactored_code, flavor
    )  # Execute visitors after refactoring

    if args.verify:
        original_function_count = len(identify_function_boundaries(code, flavor))
        new_function_count = len(identify_function_boundaries(refactored_code, flavor))
        verify_refactoring(
            "agent_functions", original_function_count, new_function_count
        )

    if args.min_functions:
        new_function_count = len(identify_function_boundaries(refactored_code, flavor))
        if new_function_count < args.min_functions:
            print(
                f"Error: Refactored code has fewer than {args.min_functions} functions."
            )
            sys.exit(1)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(refactored_code)

    if args.render_mermaid:
        api_scan = scan_code(refactored_code, flavor)
        mermaid_diagram = render_mermaid_diagram(api_scan)
        print("Mermaid Diagram:")
        print(mermaid_diagram)

    execute_visitor_plugins(refactored_code, flavor)

    logging.debug("Exiting process_file")


def main():
    """Main function of the script."""
    logging.debug("Starting main")
    args = parse_arguments()

    if args.run_example:
        example_script()
        return

    if args.run_tests:
        run_unit_tests()
        return

    path = args.path
    all_results = []
    
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(('.py', '.ts', '.js', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.rs')):
                    file_path = os.path.join(root, file)
                    results = process_file(file_path, args)
                    if results:
                        all_results.extend(results)
    else:
        results = process_file(path, args)
        if results:
            all_results.extend(results)

    if args.dsl and "FIND duplicates" in args.dsl:
        duplicates = handle_dsl_command(
            {"action": "FIND", "target": "duplicates", "params": ""}, 
            all_results, 
            ""
        )
        if duplicates:
            print("\nDuplicate Classes Found:")
            for dup in duplicates:
                print(f"\nClass '{dup['name']}' appears {dup['count']} times:")
                for inst in dup['instances']:
                    print(f"  {inst['file']}:{inst['line']} as '{inst['original_name']}'")
        else:
            print("\nNo duplicate classes found.")

    logging.debug("Main completed")

 
if __name__ == "__main__":
    logging.debug("Starting execution of line_chopping_refactor.py")
    main()
    logging.debug("Finished execution of line_chopping_refactor.py")

