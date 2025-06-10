#!/usr/bin/env python3
"""
Script to remove duplicate 'import random' statements from firebase_service.py
"""

import re

# Read the file
file_path = r'c:\Users\User\OneDrive - National ChengChi University\113-2 commucation\code\proj\app\services\firebase_service.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Split into lines
lines = content.split('\n')

# Track if we've seen the first import random (should keep the one at the top)
seen_first_import = False
new_lines = []

for i, line in enumerate(lines):
    # If this is an 'import random' line
    if line.strip() == 'import random':
        if not seen_first_import:
            # Keep the first one (at the top of the file)
            seen_first_import = True
            new_lines.append(line)
            print(f"Keeping import random at line {i+1}")
        else:
            # Skip subsequent ones
            print(f"Removing duplicate import random at line {i+1}")
            continue
    else:
        new_lines.append(line)

# Write back to file
new_content = '\n'.join(new_lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Finished removing duplicate import random statements")
