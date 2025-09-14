#!/usr/bin/env python3
"""Fix syntax errors in project_scanner.py"""

def fix_project_scanner():
    with open('x:\\GitHub\\PRJ-1\\script\\project_scanner.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the broken regex pattern line
    old_pattern = '                match = re.search(r"gem\\s+[\'"]\\w+[\'"],\\\\\\n\\*[\'"]([^\'"]+)[\'"]", content)'
    new_pattern = '                match = re.search(r"gem\\s+[\'"]\\w+[\'"],\\s*[\'"]([^\'"]+)[\'"]", content)'
    
    content = content.replace(old_pattern, new_pattern)
    
    with open('x:\\GitHub\\PRJ-1\\script\\project_scanner.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed syntax error in project_scanner.py")

if __name__ == "__main__":
    fix_project_scanner()
