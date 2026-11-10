# Remove the orphaned duplicate table block from generate_app_html.py
with open('generate_app_html.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The orphaned block is at lines 2491-2511 (1-indexed)
# That's lines[2490:2511] in 0-indexed
# Line 2489 (0-idx 2488) = '        }\n'
# Line 2490 (0-idx 2489) = '\n'  
# Lines 2491-2511 (0-idx 2490:2511) = orphan block
# Line 2512 (0-idx 2511) = '\n'
# Line 2513 (0-idx 2512) = '        function crearOTDesdeCronograma...'

# Verify
print(f"Line 2489: {lines[2488].strip()}")
print(f"Line 2490: {repr(lines[2489])}")
print(f"Line 2491: {lines[2490].strip()[:60]}")
print(f"Line 2511: {lines[2510].strip()}")
print(f"Line 2512: {repr(lines[2511])}")
print(f"Line 2513: {lines[2512].strip()[:60]}")

# Remove lines 2491-2511 (0-indexed 2490:2511)
new_lines = lines[:2490] + lines[2511:]

with open('generate_app_html.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Removed {len(lines) - len(new_lines)} orphan lines. Old: {len(lines)}, New: {len(new_lines)}")
