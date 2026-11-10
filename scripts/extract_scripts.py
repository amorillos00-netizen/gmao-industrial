# -*- coding: utf-8 -*-
with open('index.html', encoding='utf-8') as f:
    html = f.read()

import re

# Find all script blocks
scripts = re.findall(r'<script(?:\s+[^>]*)?>(.*?)</script>', html, re.DOTALL)
print(f"Total script blocks: {len(scripts)}")

# Check each script block
for i, s in enumerate(scripts):
    print(f"Script {i+1}: length = {len(s)}")
    # Write to temp file
    with open(f"scripts/temp_script_{i+1}.js", "w", encoding="utf-8") as js_file:
        js_file.write(s)
