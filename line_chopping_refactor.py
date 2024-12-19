import os
import re
import subprocess
import uuid
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Refactor Python code by chopping it into smaller functions or classes.")
    parser.add_argument("input_file", help="Path to the input Python file.")
    parser.add_argument("output_dir", help="Path to the output directory for extracted functions.")
    parser.add_argument("--refactor_config", help="Optional JSON file containing fine-grained refactoring instructions.", required=False)
    parser.add_argument("--class_only", action="store_true", help="Only extract classes, not functions.")
    parser.add_argument("--same_dir", action="store_true", help="Output extracted classes to the same directory as the input file.")


    args = parser.parse_args()

    input_file = args.input_file
    output_dir = args.output_dir
    refactor_config_file = args.refactor_config
    class_only = args.class_only
    same_dir = args.same_dir

    # Create the output directory if it doesn't exist
    if not same_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Load refactor config if provided
    refactor_config = {}
    if refactor_config_file:
        try:
            with open(refactor_config_file, "r") as f:
                refactor_config = json.load(f)
        except FileNotFoundError:
            print(f"Error: Refactor config file not found: {refactor_config_file}")
            return
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in refactor config file: {refactor_config_file}")
            return

    # Step 1: Identify function boundaries and object features
    with open(input_file, "r") as file:
        lines = file.readlines()
    
    imports = []
    for line in lines:
        if line.startswith("import ") or line.startswith("from "):
            imports.append(line)
        else:
            break

    boundaries = []
    for i, line in enumerate(lines):
        if re.match(r"(class|def) ", line):
            boundaries.append(i)
    
    boundaries.sort(reverse=True)

    # Step 2: Extract and write functions
    prev_line = 0
    function_count = 1
    modified_lines = lines[:]
    class_boundaries = [b for b in boundaries if re.match(r"class ", lines[b])]
    for start_line in boundaries:
        end_line = prev_line - 1
        
        if class_only and not re.match(r"class ", lines[start_line]):
            prev_line = start_line + 1
            continue

        # Extract the function
        if prev_line != 0:
            function_code = lines[prev_line:start_line]
        else:
            function_code = lines[:start_line]
        
        definition_line = lines[start_line]
        
        # Generate a unique ID
        unique_id = str(uuid.uuid4())
        
        # Write the function to a new file
        if same_dir:
            output_file = os.path.join(os.path.dirname(input_file), f"extracted_function_{function_count}.py")
        else:
            output_file = os.path.join(output_dir, f"extracted_function_{function_count}.py")
        with open(output_file, "w") as f:
            f.write("".join(imports))
            f.write(f"# {unique_id}\n")
            f.write(definition_line)
            f.write(f"# {unique_id}\n")
            f.write("".join(function_code))

        # Update the original class to accept the object prototype
        if start_line + 1 < len(modified_lines):
            modified_lines[start_line + 1] = re.sub(
                r"def (\w+)\(self\)", r"def \1(self, obj)", modified_lines[start_line + 1]
            )

        prev_line = start_line + 1
        function_count += 1

    # Handle the last function
    if prev_line < len(lines) and not class_only:
        function_code = lines[prev_line:]
        if function_code:
            definition_line = lines[prev_line]
            unique_id = str(uuid.uuid4())
            if same_dir:
                output_file = os.path.join(os.path.dirname(input_file), f"extracted_function_{function_count}.py")
            else:
                output_file = os.path.join(output_dir, f"extracted_function_{function_count}.py")
            with open(output_file, "w") as f:
                f.write("".join(imports))
                f.write(f"# {unique_id}\n")
                f.write(definition_line)
                f.write(f"# {unique_id}\n")
                f.write("".join(function_code[1:]))

            # Update the original class to accept the object prototype
            if prev_line + 1 < len(modified_lines):
                modified_lines[prev_line + 1] = re.sub(
                    r"def (\w+)\(self\)", r"def \1(self, obj)", modified_lines[prev_line + 1]
                )
    
    # Add seam to the beginning of the file
    if boundaries and (not class_only or class_boundaries):
        first_boundary = boundaries[0]
        unique_id = str(uuid.uuid4())
        modified_lines.insert(first_boundary, f"# {unique_id}\n")
    
    # Add seam to the end of the file
    if boundaries and (not class_only or class_boundaries):
        last_boundary = boundaries[-1]
        unique_id = str(uuid.uuid4())
        modified_lines.append(f"# {unique_id}\n")

    # Check if line counts are off
    expected_line_count = len(lines) + len([b for b in boundaries if not class_only or re.match(r"class ", lines[b])]) + (2 if [b for b in boundaries if not class_only or re.match(r"class ", lines[b])] else 0)
    if expected_line_count != len(modified_lines):
        print(f"Error: Line counts are off, aborting. Expected {expected_line_count}, got {len(modified_lines)}")
        return

    # Debug: Print the modified lines
    print("Modified lines:")
    print("".join(modified_lines))

    # Write the modified lines back to the original file
    with open(input_file, "w") as file:
        file.writelines(modified_lines)

    # Step 3: Lint the resulting files
    lint_files = [
        os.path.join(os.path.dirname(input_file) if same_dir else output_dir, f) for f in os.listdir(os.path.dirname(input_file) if same_dir else output_dir) if f.endswith(".py")
    ]
    for file in lint_files:
        try:
            subprocess.run(["black", file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error linting file {file}: {e}")

    print("Line chopping refactoring completed successfully.")

if __name__ == "__main__":
    main()
