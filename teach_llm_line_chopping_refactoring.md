# Teaching an LLM Line Chopping Refactoring

## Introduction

Line chopping refactoring is a powerful technique for improving code efficiency by breaking down large functions or classes into smaller, manageable pieces. This approach not only enhances readability but also aligns with the concept of managing **therbligs**—the basic units of work or effort in processes—to optimize performance and reduce unnecessary complexity.

## The Importance of Therbligs in Code Refactoring

In industrial engineering, therbligs represent fundamental motions or actions required to complete a task. By minimizing these units, processes become more efficient. Similarly, in code refactoring, reducing redundant or excessive code segments leads to a leaner and more efficient codebase. Embracing therblig-centric principles encourages developers to focus on essential code functionalities, eliminating superfluous elements that can hinder performance.

## Leveraging the Line Chopping Tool

The line chopping tool serves as an instrumental asset in managing therbligs within a codebase. By allowing precise selection and modification of code ranges, it enables:

- **Targeted Refactoring**: Developers can isolate and modify specific code sections without affecting the entire file.
- **Enhanced Modularity**: Breaking code into discrete, well-defined units promotes reusability and easier maintenance.
- **Reduced Cognitive Load**: Simplifying complex functions into smaller segments makes the code more approachable and understandable.

## Approach

### 1. Contextual Line Selection

The tool emphasizes the selection of code ranges based on context lines, minimizing the risk of errors during refactoring. By specifying the start and end lines, developers can accurately target the code requiring modification.

### 2. Minimizing Full Reification Errors

Full reification of code can introduce errors due to misinterpretation or misalignment of code structures. The line chopping tool mitigates this by allowing modifications within a controlled scope, preserving the integrity of the surrounding code.

### 3. Managing Indentation Challenges

In languages like Python, proper indentation is crucial. The tool ensures that extracted code fragments maintain correct indentation levels, preventing syntax errors and maintaining code consistency.

## Best Practices for Using the Line Chopping Tool

- **Precise Line Identification**: Always verify line numbers for start and end points to ensure accurate code selection.
- **Maintain Context**: Include relevant context lines to provide clarity and maintain the logical flow of the code.
- **Validate After Refactoring**: Test the modified code to ensure functionality remains unaffected.

## Minimizing Token Consumption

Certain language models have strict token limits or experience difficulties with large blocks of code. By “chopping” your code into smaller sections and providing a concise, standardized prompt element, you can guide the model more efficiently. Consider including the following points in your prompt:

• A simple overview of the line chopping objective (“We will break large code blocks into discrete segments.”).
• The main problem it solves (avoiding token overflows and confusion in large transformations).
• Instructions for how the model should handle boundary markers or context cues.

Example prompt text:
“Tool: A line-chopping utility that selectively extracts and replaces code. It reduces token overhead by fencing code regions, tracking them with unique markers, and limiting edits to vital sections only.”

## Conclusion

Incorporating therblig-centric methodologies in code refactoring leads to more efficient and maintainable codebases. The line chopping tool is an excellent resource for developers aiming to optimize their code by focusing on essential functionalities and reducing unnecessary complexities.

## Example Script

Here is an example Python script that demonstrates the line chopping refactoring process:

```python
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
with open(input_file, 'r') as file:
    lines = file.readlines()

boundaries = []
for i, line in enumerate(lines):
    if re.match(r'(class|def) ', line):
        boundaries.append(i)

# Step 2: Extract and write functions
prev_line = 0
for start_line in boundaries:
    end_line = prev_line - 1

    # Extract the function
    if prev_line != 0:
        function_code = lines[prev_line:start_line]
    else:
        function_code = lines[:start_line]

    # Generate a unique ID
    unique_id = str(uuid.uuid4())

    # Write the function to a new file
    function_name = re.search(r'(class|def) (\w+)', lines[start_line]).group(2)
    output_file = os.path.join(output_dir, f"{function_name}.py")
    with open(output_file, 'w') as f:
        f.write(''.join(function_code))

    # Add unique comment token
    with open(output_file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"# {unique_id}\n{content}")

    # Add unique comment token to the original file
    lines.insert(start_line, f"# {unique_id}\n")

    # Update the original class to accept the object prototype
    lines[start_line + 1] = re.sub(r'def (\w+)\(self\)', r'def \1(self, obj)', lines[start_line + 1])

    prev_line = start_line + 1

# Handle the last function
if prev_line != 0:
    function_code = lines[prev_line:]
    function_name = re.search(r'(class|def) (\w+)', lines[prev_line]).group(2)
    output_file = os.path.join(output_dir, f"{function_name}.py")
    with open(output_file, 'w') as f:
        f.write(''.join(function_code))

    # Add unique comment token
    with open(output_file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"# {uuid.uuid4()}\n{content}")

    # Add unique comment token to the original file
    lines.insert(prev_line, f"# {uuid.uuid4()}\n")

    # Update the original class to accept the object prototype
    lines[prev_line + 1] = re.sub(r'def (\w+)\(self\)', r'def \1(self, obj)', lines[prev_line + 1])

# Debug: Print the modified lines
print("Modified lines:")
print(''.join(lines))

# Write the modified lines back to the original file
with open(input_file, 'w') as file:
    file.writelines(lines)

# Step 3: Lint the resulting files
lint_files = [input_file] + [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.py')]
for file in lint_files:
    subprocess.run(['black', file])

print("Line chopping refactoring completed successfully.")
```

## Example Unit Tests

Here is an example Python file that includes unit tests to verify the functionality of the line chopping refactoring process:

```python
import unittest
import os
import re
import uuid
import subprocess

class TestLineChoppingRefactoring(unittest.TestCase):

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
        with open(self.input_file, 'w') as f:
            f.write(self.sample_code)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        os.remove(self.input_file)
        for file in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, file))
        os.rmdir(self.output_dir)

    def test_identify_function_boundaries(self):
        with open(self.input_file, 'r') as file:
            lines = file.readlines()
        boundaries = [i for i, line in enumerate(lines) if re.match(r'(class|def) ', line)]
        self.assertEqual(boundaries, [1, 4, 7])

    def test_extract_and_write_functions(self):
        with open(self.input_file, 'r') as file:
            lines = file.readlines()
        boundaries = [i for i, line in enumerate(lines) if re.match(r'(class|def) ', line)]
        prev_line = 0
        for start_line in boundaries:
            end_line = prev_line - 1
            function_code = lines[prev_line:start_line] if prev_line != 0 else lines[:start_line]
            unique_id = str(uuid.uuid4())
            function_name = re.search(r'(class|def) (\w+)', lines[start_line]).group(2)
            output_file = os.path.join(self.output_dir, f"{function_name}.py")
            with open(output_file, 'w') as f:
                f.write(''.join(function_code))
            with open(output_file, 'r+') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(f"# {unique_id}\n{content}")
            lines.insert(start_line, f"# {unique_id}\n")
            lines[start_line + 1] = re.sub(r'def (\w+)\(self\)', r'def \1(self, obj)', lines[start_line + 1])
            prev_line = start_line + 1
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "Supervisor.py")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "manage.py")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "report.py")))

    def test_lint_files(self):
        subprocess.run(['black', self.input_file])
        lint_files = [self.input_file] + [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if f.endswith('.py')]
        for file in lint_files:
            result = subprocess.run(['black', '--check', file], capture_output=True)
            self.assertEqual(result.returncode, 0)

if __name__ == '__main__':
    unittest.main()
```

This test suite includes tests for identifying function boundaries, extracting and writing functions, and linting the resulting files. It uses the `unittest` framework to ensure that the refactoring process works as expected.

## Example

Before:
```
1 | def add(a, b):
2 |     return a + b
3 |
4 | def subtract(a, b):
5 |     return a - b
```

After:
```
1 | # Context line: def add(a, b):
2 | def multiply(a, b):
3 |     return a * b
4 | # Context line: def subtract(a, b):
```

In this example, the lines between the context lines have been replaced with new code.

## Implementation

To implement this feature, we will need to update the line chopping tool to accept a new input format. The input format will include the context lines and the new code to replace the existing lines.

We will also need to update the tool to handle the new input format and generate the refactored code.

## Verification and Filtering

When refactoring, you can enable verification metrics and apply filters by using command-line options like --verify and --min_functions:

• --verify gathers metrics (e.g., total line count, function count) after chopping.
• --min_functions checks that the refactored file includes at least a certain number of functions, warning if the threshold is not met.

Example usage:
```bash
python line_chopping_refactor.py myfile.py --verify --min_functions=2
```

This ensures your line chopping process meets minimum expectations for function count and provides summary metrics for validation.

## Mini DSL for Line Chopping

To simplify specifying exact line ranges or function blocks, we introduce a small DSL. A typical instruction might look like:

• CHOP lines 10..30 -> extract
• CHOP def manage -> rename=administer
• CHOP class Supervisor -> rename=Manager

These instructions can be parsed and converted into concrete refactoring actions. A sample CLI call might look like:

```bash
python line_chopping_refactor.py myfile.py --dsl "CHOP lines 10..30 -> extract; CHOP def manage -> rename=administer"
```

## Code API Scanning

You can leverage the same line-chopping infrastructure to perform a “scan-only” operation. Passing a flag such as `--scan_only` utilizes the function/class boundary detection logic without extracting or modifying the source code. This enables quick identification of available APIs in a file.

Example usage:
```bash
python line_chopping_refactor.py myfile.py --scan_only
```
`````
