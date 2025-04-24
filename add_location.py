import csv
import re

# Input files
INPUT_CSV = "multi_step_problems.csv"
MARKDOWN_FILE = "toc.md"
OUTPUT_CSV = "multi_step_with_location.csv"

# Parse the markdown file and extract filename-to-title mapping
filename_to_title = {}

with open(MARKDOWN_FILE, 'r', encoding='utf-8') as md_file:
    for line in md_file:
        match = re.search(r'\[([^\]]+)\]\(\.\/html\/([^\)]+)\)', line)
        if match:
            title = match.group(1).strip()
            filename = match.group(2).strip()
            filename_to_title[filename] = title

# Read the original CSV and add the Location column
rows = []

with open(INPUT_CSV, 'r', encoding='utf-8') as csv_in:
    reader = csv.DictReader(csv_in)
    fieldnames = reader.fieldnames + ["Location"]

    for row in reader:
        filename = row["filename"].strip()
        row["Location"] = filename_to_title.get(filename, "")
        rows.append(row)

# Write the new CSV with the added Location column
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csv_out:
    writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done. Added 'Location' to {len(rows)} rows in {OUTPUT_CSV}.")
