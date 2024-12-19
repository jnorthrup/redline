import os
import re
import subprocess
import uuid

# Define the input file and output directory
input_file = "supervisor.py"
output_dir = "agent_functions"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Step 1: Identify function boundaries and object features
with open(input_file, "r") as file:
    lines = file.readlines()

boundaries = []
for i, line in enumerate(lines):
    if re.match(r"(class|def) ", line):
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
    function_name = re.search(r"(class|def) (\w+)", lines[start_line]).group(2)
    output_file = os.path.join(output_dir, f"{function_name}.py")
    with open(output_file, "w") as f:
        f.write("".join(function_code))

    # Add unique comment token
    with open(output_file, "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"# {unique_id}\n{content}")

    # Add unique comment token to the original file
    lines.insert(start_line, f"# {unique_id}\n")

    # Update the original class to accept the object prototype
    lines[start_line + 1] = re.sub(
        r"def (\w+)\(self\)", r"def \1(self, obj)", lines[start_line + 1]
    )

    prev_line = start_line + 1

# Handle the last function
if prev_line != 0:
    function_code = lines[prev_line:]
    function_name = re.search(r"(class|def) (\w+)", lines[prev_line]).group(2)
    output_file = os.path.join(output_dir, f"{function_name}.py")
    with open(output_file, "w") as f:
        f.write("".join(function_code))

    # Add unique comment token
    with open(output_file, "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"# {uuid.uuid4()}\n{content}")

    # Add unique comment token to the original file
    lines.insert(prev_line, f"# {uuid.uuid4()}\n")

    # Update the original class to accept the object prototype
    lines[prev_line + 1] = re.sub(
        r"def (\w+)\(self\)", r"def \1(self, obj)", lines[prev_line + 1]
    )

# Debug: Print the modified lines
print("Modified lines:")
print("".join(lines))

# Write the modified lines back to the original file
with open(input_file, "w") as file:
    file.writelines(lines)

# Step 3: Lint the resulting files
lint_files = [input_file] + [
    os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".py")
]
for file in lint_files:
    subprocess.run(["black", file])

print("Line chopping refactoring completed successfully.")
