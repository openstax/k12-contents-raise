import csv
import re
import sys
from pathlib import Path
from collections import defaultdict

# === Config ===
NICKNAME_PREFIX = "Alg1_"
LOG_FILE = "nickname_teks_log.txt"

# === TOC Parsing ===

def parse_toc(toc_path):
    toc_map = {}
    pattern = re.compile(r'\[(.*?)(\d+\.\d+\.\d+): (.*?)\]\(\./html/([a-f0-9\-]+\.html)\)')

    with open(toc_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                _, numeric_prefix, _, filename = match.groups()
                toc_map[filename] = {
                    'full': numeric_prefix,
                    'section': '.'.join(numeric_prefix.split('.')[:2]),
                    'nickname_middle': numeric_prefix.replace('.', '_')
                }
    return toc_map

# === TEKS Mapping ===

def load_teks_mapping(teks_path):
    mapping = defaultdict(lambda: {'TEKS': [], 'machine_readable_teks': []})
    
    with open(teks_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lesson = row['lesson'].strip()
            teks = row['Human_TEKS'].strip()
            machine = row['machine_readable'].strip()
            mapping[lesson]['TEKS'].append(teks)
            mapping[lesson]['machine_readable_teks'].append(machine)
    return mapping

# === CSV Processing ===

def process_csv(input_csv, toc_map, teks_map, output_csv):
    errors = []

    with open(input_csv, 'r', encoding='utf-8') as infile, \
         open(output_csv, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['nickname', 'TEKS', 'machine_readable_teks']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            filename = row.get('filename', '').strip()
            multi_step_id = row.get('multi_step_id', '').strip()
            nickname, teks, machine_teks = '', '', ''

            if not multi_step_id:
                errors.append(f"Missing multi_step_id for filename: {filename}")
            
            if filename in toc_map:
                toc_info = toc_map[filename]
                nickname = f"{NICKNAME_PREFIX}{toc_info['nickname_middle']}_{multi_step_id}"
                lesson_key = toc_info['section']

                if lesson_key in teks_map:
                    teks = ','.join(sorted(set(teks_map[lesson_key]['TEKS'])))
                    machine_teks = ','.join(sorted(set(teks_map[lesson_key]['machine_readable_teks'])))
                else:
                    errors.append(f"No TEKS mapping found for lesson section: {lesson_key}")
            else:
                errors.append(f"Filename not found in TOC: {filename}")

            row['nickname'] = nickname
            row['TEKS'] = teks
            row['machine_readable_teks'] = machine_teks
            writer.writerow(row)

    if errors:
        with open(LOG_FILE, 'w', encoding='utf-8') as log:
            log.write('\n'.join(errors))
        print(f"⚠️  {len(errors)} issues logged to {LOG_FILE}")
    else:
        print("✅ No errors encountered.")

# === Entry Point ===

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python nickname_and_teks.py <input_csv> <toc_md> <teks_mapping_csv> <output_csv>")
        sys.exit(1)

    input_csv = Path(sys.argv[1])
    toc_md = Path(sys.argv[2])
    teks_csv = Path(sys.argv[3])
    output_csv = Path(sys.argv[4])

    toc_map = parse_toc(toc_md)
    teks_map = load_teks_mapping(teks_csv)
    process_csv(input_csv, toc_map, teks_map, output_csv)
    print(f"✅ Output written to {output_csv}")