# Teaching an LLM Line Chopping Refactoring

## Introduction

Line chopping refactoring is a technique used to break down large functions or classes into smaller, more manageable pieces. This process involves extracting functions, adding unique identifiers, and ensuring that the code remains functional and well-structured. This document outlines the steps and considerations for teaching an LLM (Language Model) to perform line chopping refactoring.

## Steps to Teach the LLM

### 1. Understand the Code Structure

- **Identify Function Boundaries**: The LLM should be able to identify the boundaries of functions and classes in the code. This can be done using regular expressions to match `class` and `def` keywords.
- **Extract Function Code**: Once the boundaries are identified, the LLM should extract the code for each function or class.

### 2. Generate Unique Identifiers

- **Generate Unique IDs**: For each extracted function, the LLM should generate a unique identifier (e.g., a UUID) to ensure that each function can be uniquely identified.
- **Add Comment Tokens**: The LLM should add a unique comment token at the beginning of each extracted function and in the original file to maintain a reference.

### 3. Write Extracted Functions to New Files

- **Create Output Directory**: The LLM should create an output directory to store the extracted functions.
- **Write Functions**: The LLM should write each extracted function to a new file in the output directory, ensuring that the file names are meaningful (e.g., `function_name.py`).

### 4. Update Original File

- **Insert Comment Tokens**: The LLM should insert the unique comment tokens at the appropriate locations in the original file to maintain a reference to the extracted functions.
- **Update Function Signatures**: The LLM should update the function signatures in the original file to accept an additional parameter (e.g., `obj`) to pass the necessary context to the extracted functions.

### 5. Lint and Format the Code

- **Lint the Files**: The LLM should use a code linter (e.g., `black` for Python) to ensure that the extracted functions and the original file are properly formatted and adhere to coding standards.
- **Handle Linting Errors**: The LLM should handle any linting errors and ensure that the code is clean and well-structured.

### 6. Test the Refactored Code

- **Run Tests**: The LLM should run the existing tests to ensure that the refactored code still functions as expected.
- **Manual Verification**: The LLM should provide a manual verification step to ensure that the refactored code meets the requirements and does not introduce any bugs.

## Considerations

- **Error Handling**: The LLM should handle any errors that occur during the refactoring process, such as syntax errors or linting issues.
- **Code Quality**: The LLM should ensure that the refactored code maintains or improves the overall code quality.
- **Documentation**: The LLM should update any relevant documentation to reflect the changes made during the refactoring process.

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

## Conclusion

By following these steps and considerations, an LLM can be effectively taught to perform line chopping refactoring. This process not only breaks down large functions into smaller, more manageable pieces but also ensures that the code remains functional, well-structured, and adheres to coding standards.
