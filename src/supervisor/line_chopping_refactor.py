import subprocess
from typing import List, Tuple, Dict, Optional
import re

class IndentContext:
    def __init__(self, base_indent: str = ''):
        self.base_indent = base_indent
        self.current_indent = base_indent

    def matches_indent(self, line: str) -> bool:
        return line.startswith(self.current_indent)

def get_indent_level(line: str) -> str:
    match = re.match(r'^(\s*)', line)
    return match.group(1) if match else ''

def get_function_boundaries(file_path: str) -> List[Tuple[int, str, str]]:
    """Get function boundaries with indent context."""
    # Initial grep for def/class with context
    cmd = f"""grep -n -A1 '^[[:space:]]*(def|class)[[:space:]]+' {file_path} | \
             grep -v '^--$'"""
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    raw_matches = result.stdout.splitlines()
    
    boundaries = []
    i = 0
    while i < len(raw_matches):
        # Parse definition line
        def_line = raw_matches[i]
        line_num, content = def_line.split(':', 1)
        line_num = int(line_num)
        
        # Get indent of body (next line)
        if i + 1 < len(raw_matches):
            body_line = raw_matches[i + 1].split(':', 1)[1]
            body_indent = get_indent_level(body_line)
        else:
            body_indent = get_indent_level(content) + '    '
            
        boundaries.append((line_num, content.strip(), body_indent))
        i += 2
        
    return boundaries

def find_section_end(file_path: str, start_line: int, body_indent: str) -> Optional[int]:
    """Find end of indented section using grep."""
    # Search for next line with same or less indentation
    cmd = f"""tail -n+{start_line + 1} {file_path} | \
             grep -n -m1 '^[[:space:]]*[^[:space:]]' || true"""
             
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if not result.stdout:
        return None
        
    end_offset, line = result.stdout.split(':', 1)
    if get_indent_level(line) <= body_indent:
        return start_line + int(end_offset)
    return None

def edit_section(file_path: str, start: int, end: int, new_content: str, 
                preserve_indent: bool = True) -> None:
    """Edit file section using process substitution with indent preservation."""
    if preserve_indent:
        # Get original indentation
        cmd = f"sed -n '{start}p' {file_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        original_indent = get_indent_level(result.stdout)
        
        # Apply indentation to new content
        new_content = '\n'.join(
            original_indent + line if line.strip() else line 
            for line in new_content.splitlines()
        )
    
    if start > 1:
        head_cmd = f"head -n{start-1} {file_path}"
    else:
        head_cmd = "true"
        
    if end:
        tail_cmd = f"tail -n+{end+1} {file_path}"
    else:
        tail_cmd = "true"
        
    cmd = f"""cat <(eval "{head_cmd}") \
                 <(echo "{new_content}") \
                 <(eval "{tail_cmd}") > {file_path}.tmp && \
             mv {file_path}.tmp {file_path}"""
    
    subprocess.run(cmd, shell=True, check=True)

def efficient_edit(file_path: str, edits: List[Dict[str, str]]) -> None:
    """Perform edits with indent awareness."""
    boundaries = get_function_boundaries(file_path)
    
    for edit in edits:
        if edit['type'] == 'function':
            for i, (line_num, content, body_indent) in enumerate(boundaries):
                if edit['target'] in content:
                    end_line = find_section_end(file_path, line_num, body_indent)
                    edit_section(
                        file_path, 
                        line_num, 
                        end_line,
                        edit['content'],
                        preserve_indent=True
                    )
                    break

def validate_indentation(file_path: str) -> bool:
    """Validate Python indentation integrity."""
    cmd = """awk '
        /^[[:space:]]*def|^[[:space:]]*class/ { 
            if (indent_level[$0] != "") 
                exit 1
            indent_level[$0] = length($0) - length(ltrim($0))
        }
        END { exit 0 }
    ' """ + file_path
    
    return subprocess.run(cmd, shell=True).returncode == 0