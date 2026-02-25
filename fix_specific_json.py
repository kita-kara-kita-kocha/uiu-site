#!/usr/bin/env python3
import json
import re

def fix_niconico_duplicates(file_path):
    """Fix duplicate patterns specifically in niconico_l.json"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Fixing {file_path}...")
    
    # Pattern 1: Remove duplicate upload_date and metadata sections
    content = re.sub(
        r'(\s+"upload_date": "[0-9/]+")(\s+)(\],\s+"upload_date": "[0-9/]+")',
        r'\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Pattern 2: Remove duplicate metadata entries within arrays
    content = re.sub(
        r'(\s+"放送開始: [^"]+"),\s+("放送開始: [^"]+"),',
        r'\1,',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 3: Fix malformed arrays - remove extra closing brackets
    content = re.sub(
        r'(\s+"upload_date": "[0-9/]+")(\s+\],\s+"upload_date": "[0-9/]+")',
        r'\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Pattern 4: Clean up any hanging metadata arrays
    lines = content.split('\n')
    cleaned_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip obvious duplicate lines
        if i > 0 and line.strip() and line == lines[i-1]:
            i += 1
            continue
            
        # Check for duplicate upload_date pattern
        if '"upload_date":' in line and i < len(lines) - 1:
            # Look ahead for duplicate
            j = i + 1
            while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith(']') or lines[j].strip().startswith('"')):
                if '"upload_date":' in lines[j]:
                    # Skip the duplicate
                    break
                j += 1
            if j < len(lines) and '"upload_date":' in lines[j]:
                # Skip all lines until the duplicate is processed
                cleaned_lines.append(line)
                i = j
                continue
        
        cleaned_lines.append(line)
        i += 1
    
    content = '\n'.join(cleaned_lines)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Applied fixes to {file_path}")

def fix_fciu_duplicates(file_path):
    """Fix duplicate patterns specifically in fciu.json"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Fixing {file_path}...")
    
    # Remove duplicate metadata entries
    content = re.sub(
        r'(\s+"無料部分 [^"]+")(\s+"配信日時: [^"]+",\s+"再生時間: [^"]+",\s+"再生回数: [^"]+",\s+"視聴条件: [^"]+",\s+"無料部分 [^"]+")(\s+\])',
        r'\1\3',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Remove duplicate image/upload_date fields
    content = re.sub(
        r'(\s+"image": "[^"]+",\s+"upload_date": "[^"]+",)(\s+"image": "[^"]+",\s+"upload_date": "[^"]+",)',
        r'\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Applied fixes to {file_path}")

def validate_json(file_path):
    """Validate JSON and show specific errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✓ {file_path} is valid")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ {file_path} error at line {e.lineno}: {e.msg}")
        return False

if __name__ == "__main__":
    # Fix niconico_l.json
    fix_niconico_duplicates('docs/niconico_l.json')
    validate_json('docs/niconico_l.json')
    
    # Fix fciu.json  
    fix_fciu_duplicates('docs/fciu.json')
    validate_json('docs/fciu.json')