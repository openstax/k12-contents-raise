import os
import re
import shutil

# Paths
toc_path = '../../../toc.md'
html_dir = '../../../html'
output_dir = 'warmups'

# Make sure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Regular expression to match warm-up lesson format (e.g. 1.1.1:, 2.3.1:, etc.)
warmup_pattern = re.compile(r'\[\s*(\d+\.\d+\.1):.*\]\(\./html/([a-f0-9\-]+\.html)\)')

# Track whether we are inside a Teacher Guide section
inside_teacher_guide = False

# Collect warm-up links
with open(toc_path, 'r') as toc_file:
    for line in toc_file:
        # Check if we are entering or exiting a Teacher Guide section
        if "Teacher Guide" in line:
            inside_teacher_guide = True
            continue
        if line.startswith("    * ") or line.startswith("* "):
            inside_teacher_guide = False

        # Only process if not in Teacher Guide
        if not inside_teacher_guide:
            match = warmup_pattern.search(line)
            if match:
                hash_filename = match.group(2)
                src = os.path.join(html_dir, hash_filename)
                dst = os.path.join(output_dir, hash_filename)

                # Copy if file exists
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    print(f"Copied: {hash_filename}")
                else:
                    print(f"Missing file: {hash_filename}")

print(f"\n✅ All warm-up student files copied to '{output_dir}'")