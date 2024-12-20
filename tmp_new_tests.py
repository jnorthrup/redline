
    def test_nested_class_boundary_detection(self):
        nested_class_code = '''
class OuterClass:
    def __init__(self):
        pass
    class InnerClass:
        def __init__(self):
            pass
        def inner_method(self):
            pass
    def outer_method(self):
        pass
'''
        with open(self.test_file_path, 'w') as f:
            f.write(nested_class_code)
        boundaries = self._get_function_boundaries(self.test_file_path)
        expected_boundaries = {
            'OuterClass': (2, 10),
            'OuterClass.__init__': (3, 4),
            'OuterClass.InnerClass': (5, 8),
            'OuterClass.InnerClass.__init__': (6, 7),
            'OuterClass.InnerClass.inner_method': (8, 8),
            'OuterClass.outer_method': (10, 10),
        }
        self.assertEqual(boundaries, expected_boundaries)

    def test_chop_and_rewrite_with_indentation(self):
        import tempfile

        code = '''
def outer_function(x):
    if x > 5:
        def inner_function(y):
            return y * 2
        return inner_function(x) + 1
    else:
        return x - 1
'''
        with open(self.test_file_path, 'w') as f:
            f.write(code)

        # Identify the outer_function
        from redline.supervisor.line_chopping_refactor import \
            identify_function_boundaries
        functions = identify_function_boundaries(code)
        outer_function = next(func for func in functions if func['name'] == 'outer_function')

        # Create a temp file for the original code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        # Define the start and end lines for the middle section
        start_line = outer_function['start_line'] + 2
        end_line = outer_function['end_line'] - 1

        # Define the new middle code
        new_middle_code = '''
    if x > 10:
        return x + 10
    else:
        return x - 10
'''

        # Construct the head, middle, and tail commands
        head_command = fhead-n{start_line-1}{tmp_file_path}
        middle_command = fecho{new_middle_code.strip()}
        tail_command = ftail-n+{end_line+1}{tmp_file_path}

        # Execute the commands and combine the output
        from subprocess import check_output
        head_output = check_output(head_command, shell=True).decode('utf-8').strip()
        middle_output = check_output(middle_command, shell=True).decode('utf-8').strip()
        tail_output = check_output(tail_command, shell=True).decode('utf-8').strip()

        rewritten_code = f'{head_output}\n{middle_output}\n{tail_output}'

        # Verify that the rewritten code is correct
        expected_rewritten_code = '''def outer_function(x):
    if x > 10:
        return x + 10
    else:
        return x - 10
'''
        self.assertEqual(rewritten_code, expected_rewritten_code)

        # Clean up temp file
        os.remove(tmp_file_path)
