#!/usr/bin/env python3
import json
import re

def fix_json_file(file_path):
    """Fix duplicate entries and missing commas in JSON file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Fixing {file_path}...")
    
    # 1. Fix missing commas after quoted strings (general pattern)
    content = re.sub(
        r'(".*?")\n(\s+".*?":)',
        r'\1,\n\2',
        content,
        flags=re.MULTILINE
    )
    
    # 2. Remove duplicate consecutive metadata entries
    # Pattern: "line1", "line2" followed by duplicate "line1", "line2"
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check for duplicate pattern in arrays
        if '        "' in line and line.strip().endswith('",'):
            # Look for potential duplicate sequence
            current_entry = line.strip()
            j = i + 1
            
            # Collect next few lines in the array
            array_lines = [current_entry]
            while j < len(lines) and '        "' in lines[j] and lines[j].strip().endswith(('",', '"')):
                array_lines.append(lines[j].strip())
                j += 1
            
            # Check if the next sequence is identical
            k = j
            duplicate_lines = []
            while k < len(lines) and len(duplicate_lines) < len(array_lines) and '        "' in lines[k] and lines[k].strip() in array_lines:
                duplicate_lines.append(lines[k].strip())
                k += 1
            
            # If we found a complete duplicate sequence, skip it
            if duplicate_lines == array_lines:
                # Skip the duplicate lines
                for _ in range(len(array_lines) - 1):  # -1 because we already added the first line
                    if j < len(lines):
                        new_lines.append(lines[j])
                        j += 1
                i = k - 1  # Skip the duplicate sequence
            else:
                # Add the rest of the array lines normally
                for idx in range(j - i - 1):  # Skip the line we already added
                    if i + 1 + idx < len(lines):
                        new_lines.append(lines[i + 1 + idx])
                i = j - 1
        
        i += 1
    
    content = '\n'.join(new_lines)
    
    # 3. Remove duplicate field entries (title, video_url, image, etc.)
    # Pattern: same field appearing twice in a row
    content = re.sub(
        r'(\s+"title": ".*?"),\n(\s+"video_url": ".*?"),\n(\s+"image": ".*?"),\n\s+"title": ".*?",\n\s+"video_url": ".*?",\n\s+"image": ".*?",',
        r'\1,\n\2,\n\3,',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Save the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

def validate_json(file_path):
    """Validate JSON syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✓ {file_path} is now valid!")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ {file_path} still has errors: {e}")
        
        # Show specific error location
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if e.lineno <= len(lines):
                error_line = e.lineno - 1
                print(f"Error at line {e.lineno}: {lines[error_line].strip()}")
                if error_line > 0:
                    print(f"Previous line: {lines[error_line-1].strip()}")
                if error_line + 1 < len(lines):
                    print(f"Next line: {lines[error_line+1].strip()}")
        return False

if __name__ == "__main__":
    files_to_fix = ['docs/niconico_l.json', 'docs/fciu.json']
    
    for file_path in files_to_fix:
        fix_json_file(file_path)
        validate_json(file_path)