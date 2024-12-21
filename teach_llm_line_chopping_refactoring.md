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

### 4. Enhanced Tracing for Refactoring

With the integration of detailed logging, all functions in `line_chopping_refactor.py` now perform tracing analysis through their execution flow. This involves:

- **Entry and Exit Logs**: Each function logs when it is entered and exited, providing a clear trace of the execution sequence.
- **Function Execution Flow**: By examining the logs, developers can understand the order in which functions are called and how data flows through the refactoring process.
- **Debugging Assistance**: Enhanced tracing aids in identifying bottlenecks or unexpected behaviors within the refactoring tool, facilitating quicker debugging and optimization.

```python
import logging

def some_function():
    logging.debug("Entering some_function")
    # ...existing code...
    logging.debug("Exiting some_function")
```

This comprehensive logging setup ensures that the refactoring tool's operations are transparent and easily monitorable, thereby improving maintainability and reliability.

## Scope Hierarchy and Refactoring Primitives

### Scopes and Regex Parameters

- **Function Scope**
  - **Regex Pattern**: `r'def\s+(\w+)\s*\('`
  - **Description**: Identifies function declarations.

- **Class Scope**
  - **Regex Pattern**: `r'class\s+(\w+)\s*\('`
  - **Description**: Identifies class declarations.

- **Variable Scope**
  - **Regex Pattern**: `r'(\w+)\s*='`
  - **Description**: Identifies variable assignments.

### Refactoring Primitives

- **CHOP lines L..R -> extract**
  - **Description**: Extracts lines from L to R into a new function or class.

- **CHOP def function_name -> rename=new_name**
  - **Description**: Renames the specified function.

- **CHOP class ClassName -> rename=NewName**
  - **Description**: Renames the specified class.

## Restructuring for DSL Integration

To align the document with the DSL (Domain-Specific Language) framework, the following restructuring is implemented:

### DSL Overview

The DSL is designed to simplify and standardize refactoring commands, allowing developers to specify refactoring actions concisely. It integrates seamlessly with the line chopping tool, enabling automated and precise code modifications.

### DSL Syntax and Semantics

- **CHOP lines L..R -> extract**: Extracts lines from L to R into a new function or class.
- **CHOP def function_name -> rename=new_name**: Renames the specified function.
- **CHOP class ClassName -> rename=NewName**: Renames the specified class.
- **CHOP lines L..R -> migrate_manual_steps**: Automates manual refactoring steps within the specified lines.
- **CHOP def function_name -> integrate_custom_action**: Integrates custom refactoring actions for the specified function.

**Examples:**

```bash
python line_chopping_refactor.py myfile.py --dsl "CHOP lines 10..30 -> extract; CHOP def manage -> rename=administer; CHOP class Supervisor -> rename=Manager"
```

### DSL Integration in Refactoring

The DSL commands are parsed through "process_dsl_instructions" to handle all refactoring tasks in a unified manner.

## Inventory of Non-DSL Code

Identify sections and code snippets within the document and tool that are now represented by the DSL:

- **Manual Refactoring Steps**: Previously described manual processes are now automated through DSL commands like `migrate_manual_steps`.
- **Custom Refactoring Actions**: Specific actions such as integrating custom behaviors are now manageable via DSL commands like `integrate_custom_action`.
- **Utility Functions in Tool**: Enhanced utility functions support DSL-driven operations, ensuring seamless execution of refactoring commands.

## Gradient Analysis for DSL Migration

Analyze the identified non-DSL elements to prioritize their migration into the DSL framework:

1. **High Priority**
   - **Manual Refactoring Steps**
     - **Reason**: Automating these steps can significantly improve efficiency.
     - **Action**: Define corresponding DSL commands to automate these processes.

2. **Medium Priority**
   - **Utility Functions in Tool**
     - **Reason**: Enhancing tool capabilities through DSL can streamline operations.
     - **Action**: Integrate these utilities as callable DSL actions.

3. **Low Priority**
   - **Custom Refactoring Actions**
     - **Reason**: These actions are rarely used and have minimal impact.
     - **Action**: Evaluate the necessity before DSL integration.

## Best Practices for Using the Line Chopping Tool

- **Precise Line Identification**: Always verify line numbers for start and end points to ensure accurate code selection.
- **Maintain Context**: Include relevant context lines to provide clarity and maintain the logical flow of the code.
- **Validate After Refactoring**: Test the modified code to ensure functionality remains unaffected.
- **Leverage Enhanced Tracing**: Utilize the detailed logging to monitor the refactoring process and diagnose issues effectively.
- **Utilize DSL Commands**: Prefer using DSL commands for refactoring to maintain consistency and leverage automation benefits.

## Minimizing Token Consumption

Certain language models have strict token limits or experience difficulties with large blocks of code. By “chopping” your code into smaller sections and providing a concise, standardized prompt element, you can guide the model more efficiently. Consider including the following points in your prompt:

• A simple overview of the line chopping objective (“We will break large code blocks into discrete segments.”).

• The main problem it solves (avoiding token overflows and confusion in large transformations).

• Instructions for how the model should handle boundary markers or context cues.

Example prompt text:
“We will add detailed logging to trace the execution flow of the line chopping refactoring tool. This includes entry and exit logs for each function, along with key variable states.”

## Common DSL Examples

Here are some common DSL examples to illustrate how to use the line chopping tool effectively:

### Extracting Lines into a New Function

To extract lines 10 to 30 into a new function:

```bash
python line_chopping_refactor.py myfile.py --dsl "CHOP lines 10..30 -> extract"
```

### Renaming a Function

To rename a function `manage` to `administer`:

```bash
python line_chopping_refactor.py myfile.py --dsl "CHOP def manage -> rename=administer"
```

### Renaming a Class

To rename a class `Supervisor` to `Manager`:

```bash
python line_chopping_refactor.py myfile.py --dsl "CHOP class Supervisor -> rename=Manager"
```

### Migrating Manual Refactoring Steps

To automate manual refactoring steps within lines 50 to 70:

```bash
python line_chopping_refactor.py myfile.py --dsl "CHOP lines 50..70 -> migrate_manual_steps"
```

### Integrating Custom Refactoring Actions

To integrate custom refactoring actions for the function `process_data`:

```bash
python line_chopping_refactor.py myfile.py --dsl "CHOP def process_data -> integrate_custom_action"
```

## Editing Scenarios: Prepend, Append, and Concatenation

### Prepend

Prepending involves adding code at the beginning of a file or function. This can be useful for adding imports, comments, or initial setup code.

Example:

```python
# Prepend logging setup to a Python file
import logging

logging.basicConfig(level=logging.DEBUG)

# ...existing code...
```

### Append

Appending involves adding code at the end of a file or function. This is often used for adding cleanup code, final comments, or closing statements.

Example:

```python
# Append a closing statement to a Python function
def some_function():
    # ...existing code...
    logging.debug("Exiting some_function")
```

### Concatenation

Concatenation using `cat <() <() <()` allows combining multiple files or code snippets into a single output. This is useful for merging code from different sources or creating a composite script.

Example:

```bash
# Concatenate three Python files into one
cat <(echo "# Combined Script") <(cat file1.py) <(cat file2.py) <(cat file3.py) > combined.py
```

## Conclusion

Incorporating therblig-centric methodologies in code refactoring leads to more efficient and maintainable codebases. The line chopping tool, now enhanced with detailed tracing capabilities, is an excellent resource for developers aiming to optimize their code by focusing on essential functionalities and reducing unnecessary complexities.

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
        with open(self.input_file, 'r') as file):
            lines = file.readlines()
        boundaries = [i for i, line in enumerate(lines) if re.match(r'(class|def) ', line)]
        self.assertEqual(boundaries, [1, 4, 7])

    def test_extract_and_write_functions(self):
        with open(self.input_file, 'r') as file):
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

## Including File Objects in UML Interactions

The line chopping tool can visualize the interactions between file objects and their transformations using UML diagrams. This helps in understanding the 1-to-many conversion per the DSL commands.

### Visualizing File Objects

To include file objects in the UML interactions, the tool generates diagrams that show how a single file can be split into multiple smaller files. This is particularly useful for understanding the impact of refactoring on the codebase structure.

### Example

Here is an example of how a single file can be split into multiple files:

```bash
# Render the UML diagram showing file objects
python line_chopping_refactor.py myfile.py --dsl "CHOP lines 10..30 -> extract; CHOP def manage -> rename=administer" --render_mermaid
```

This command applies the specified DSL commands and generates a UML diagram that includes the file objects and their transformations.

## Propose Mode for DSL

The "propose" mode allows running graphics visitors without applying mutation visitors. This is useful for visualizing the proposed changes without actually modifying the code.

### Propose Mode Overview

In propose mode, the tool processes the DSL commands and generates the corresponding UML diagrams without making any changes to the code. This helps in reviewing the proposed refactoring before committing to the changes.

### Example

Here is an example of using propose mode:

```bash
# Run in propose mode to visualize the proposed changes
python line_chopping_refactor.py myfile.py --dsl "CHOP lines 10..30 -> extract; CHOP def manage -> rename=administer" --propose --render_mermaid
```

This command processes the DSL commands in propose mode and generates a UML diagram showing the proposed changes.

### Benefits of Propose Mode

- **Review Before Commit**: Allows developers to review the proposed changes before applying them.
- **Visual Feedback**: Provides visual feedback on the impact of the refactoring.
- **Safe Exploration**: Enables safe exploration of different refactoring options without modifying the code.

By using propose mode, developers can ensure that the refactoring aligns with their goals and make informed decisions about the changes.

## New Visitor Plugins

Three new visitor plugins have been introduced to enhance the refactoring workflow:

1. **BashToolsVisitor**: Handles external bash tools.
2. **DSLVisualizationVisitor**: Renders before-and-after diagrams for DSL refactoring steps.
3. **ReviewLatchVisitor**: Provides a review checkpoint to accept or reject proposed changes before finalizing.
4. **MetricsLoggerVisitor**: Integrates pandas-based metrics logging to monitor and analyze refactoring performance on demand.

These plugins are registered in sequence to allow the BashToolsVisitor to run first, followed by visualization, metrics logging, and then the final review latch.

## Metrics Logging

The **MetricsLoggerVisitor** utilizes pandas to collect and transform metrics related to the refactoring process. It can be triggered at any point to generate reports and analyze performance data.

### Features

- **Real-time Metrics Collection**: Gathers data during the refactoring process.
- **On-Demand Reporting**: Generates detailed metrics reports when needed.
- **Data Transformation**: Uses pandas for efficient data manipulation and analysis.

### Usage

To trigger metrics logging, ensure that the MetricsLoggerVisitor is registered and invoked appropriately within the refactoring workflow.
