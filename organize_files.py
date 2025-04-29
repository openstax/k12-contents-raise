import os
import re
import shutil
from collections import defaultdict

# Define paths
toc_path = "toc.md"
html_dir = "html"
logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)

# Output directories
categories = {
    "warmups": "grouped_html/warmups/all",
    "primary_learning_activities": "grouped_html/primary_learning_activities/all",
    "additional_resources": "grouped_html/additional_resources/all",
    "cooldowns": "grouped_html/cooldowns/all",
    "practice_problems": "grouped_html/practice_problems/all",
}
for path in categories.values():
    os.makedirs(path, exist_ok=True)

# Logging setup
error_log_path = os.path.join(logs_dir, "error_log.txt")
manifest_path = os.path.join(logs_dir, "file_manifest.txt")
summary_path = os.path.join(logs_dir, "summary_report.txt")

# Clear previous logs
open(error_log_path, "w").close()
open(manifest_path, "w").close()
open(summary_path, "w").close()

def log_error(msg):
    with open(error_log_path, "a", encoding="utf-8") as log:
        log.write(msg + "\n")

def log_manifest(msg):
    with open(manifest_path, "a", encoding="utf-8") as log:
        log.write(msg + "\n")

def log_summary(msg):
    with open(summary_path, "a", encoding="utf-8") as log:
        log.write(msg + "\n")

# Read toc
with open(toc_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

unit_pattern = re.compile(r"\* Unit (\d+):")
student_lesson_pattern = re.compile(r"\* Lesson (\d+\.\d+): (?!.*Teacher Guide).*")
item_pattern = re.compile(r'\[\s*(\d+\.\d+\.\d+):?\s*(.*?)\s*\]\(\.\/html\/([a-z0-9\-]+\.html)\)', re.IGNORECASE)

current_unit = None
in_student_lesson = False
lesson_lines = []
lesson_title = ""
unit_number = 0
summary_counts = defaultdict(lambda: defaultdict(int))

def classify_and_copy_lesson(lesson_title, lesson_lines):
    lesson_items = []
    for line in lesson_lines:
        m = item_pattern.search(line)
        if m:
            num, name, fname = m.groups()
            name = name.strip()
            if "self check" in name.lower():
                continue  # skip self checks
            lesson_items.append((num, name, fname))


    if (
        not lesson_items
        or not any(n.endswith(".0") for n, _, _ in lesson_items)
        or not any(kw in lesson_items[-1][1].lower() for kw in ["lesson summary", "lesson synthesis"])
    ):
        log_error(f"Skipping {lesson_title}: missing overview or summary")
        log_summary(f"{lesson_title}\n  Skipped: Missing overview or summary\n")
        return

    overview = lesson_items[0]
    summary = lesson_items[-1]
    practice = lesson_items[-2]
    if "practice" not in practice[1].lower():
        log_error(f"Skipping {lesson_title}: second-to-last item is not Practice")
        log_summary(f"{lesson_title}\n  Skipped: Missing or misplaced practice problem\n")
        return

    # Extract relevant segments
    pre_practice_items = lesson_items[1:-2]
    practice_files = [practice]
    summary_files = [summary]

    # Categorize
    additional_resources = []
    primary_activities = []
    warmups = []
    cooldowns = []

    idx = 0
    # Identify additional resources
    while idx < len(pre_practice_items):
        if "additional resources" in pre_practice_items[idx][1].lower():
            additional_resources.append(pre_practice_items[idx])
        idx += 1

    # Identify PLAs
    for res in additional_resources:
        match_index = pre_practice_items.index(res)
        if match_index > 0:
            pla_candidate = pre_practice_items[match_index - 1]
            if pla_candidate[0].rsplit(".", 1)[0] == res[0].rsplit(".", 1)[0]:
                primary_activities.append(pla_candidate)

    # Warmups = between overview and first PLA
    if primary_activities:
        first_pla_index = pre_practice_items.index(primary_activities[0])
        warmups = pre_practice_items[:first_pla_index - len([r for r in pre_practice_items[:first_pla_index] if r in additional_resources])]

    # Cooldowns = between last AR and practice
    if additional_resources:
        last_ar_index = pre_practice_items.index(additional_resources[-1])
        cooldowns = pre_practice_items[last_ar_index + 1:]
        cooldowns = [c for c in cooldowns if c not in primary_activities]

    category_map = {
        "warmups": warmups,
        "primary_learning_activities": primary_activities,
        "additional_resources": additional_resources,
        "cooldowns": cooldowns,
        "practice_problems": practice_files,
    }

    log_summary(f"{lesson_title}")
    for cat, items in category_map.items():
        summary_counts[lesson_title][cat] += len(items)
        log_summary(f"  {cat.replace('_', ' ').title()}: {len(items)}")
        for num, name, fname in items:
            src = os.path.join(html_dir, fname)
            dst = os.path.join(categories[cat], fname)
            if os.path.exists(dst):
                log_error(f"Duplicate found: {fname}")
            if os.path.exists(src):
                shutil.copy(src, dst)
                log_manifest(f"{num}: {name} → {categories[cat]}")
            else:
                log_error(f"Missing file: {fname}")

# Parse lines
i = 0
unit_number = 0
in_student_lesson = False
in_teacher_section = False
teacher_indent_level = None
lesson_lines = []
lesson_title = ""
student_lesson_prefix = ""

def get_indent_level(line):
    return len(line) - len(line.lstrip(" "))

while i < len(lines):
    raw_line = lines[i]
    line = raw_line.strip()
    indent = get_indent_level(raw_line)

    unit_match = re.match(r"\* Unit (\d+):", line)
    lesson_match = re.match(r"\* Lesson (\d+\.\d+)[ :]+(?!Teacher Guide).*", line)
    teacher_guide_match = re.match(r"\* Lesson (\d+\.\d+)[ :]+Teacher Guide.*", line)

    if unit_match:
        unit_number = int(unit_match.group(1))
        in_student_lesson = False
        in_teacher_section = False
        lesson_lines = []
        lesson_title = ""
    elif teacher_guide_match:
        # 💥 FLUSH any active Student Lesson FIRST
        if in_student_lesson and lesson_lines:
            lessons_by_prefix = defaultdict(list)
            for l in lesson_lines:
                m = item_pattern.search(l)
                if m:
                    num, name, fname = m.groups()
                    prefix = ".".join(num.split(".")[:2])
                    lessons_by_prefix[prefix].append(l)
            for prefix, lines_group in lessons_by_prefix.items():
                classify_and_copy_lesson(f"{lesson_title} ({prefix})", lines_group)

        # 🔥 Reset clean
        in_teacher_section = True
        in_student_lesson = False
        lesson_lines = []
        lesson_title = ""
        teacher_indent_level = indent
    elif in_teacher_section:
        # If we hit a new student lesson, exit Teacher Guide mode
        if lesson_match:
            in_teacher_section = False
        elif indent > teacher_indent_level:
            # Still inside Teacher Guide -> truly skip
            i += 1
            continue
        else:
            # Unexpected outdent -> exit Teacher Guide mode
            in_teacher_section = False

    if not in_teacher_section and lesson_match and unit_number in range(1, 10):
        # 💥 FLUSH previous Student Lesson if any
        if in_student_lesson and lesson_lines:
            lessons_by_prefix = defaultdict(list)
            for l in lesson_lines:
                m = item_pattern.search(l)
                if m:
                    num, name, fname = m.groups()
                    prefix = ".".join(num.split(".")[:2])
                    lessons_by_prefix[prefix].append(l)
            for prefix, lines_group in lessons_by_prefix.items():
                classify_and_copy_lesson(f"{lesson_title} ({prefix})", lines_group)

        # 🆕 Start fresh Student Lesson
        lesson_title = lesson_match.group(0).lstrip("* ").strip()
        student_lesson_prefix = lesson_match.group(1)
        lesson_lines = []
        in_student_lesson = True
    elif in_student_lesson and not in_teacher_section and line.startswith("* ["):
        lesson_lines.append(line)

    i += 1

# Final flush at end of file
if in_student_lesson and lesson_lines:
    lessons_by_prefix = defaultdict(list)
    for l in lesson_lines:
        m = item_pattern.search(l)
        if m:
            num, name, fname = m.groups()
            prefix = ".".join(num.split(".")[:2])
            lessons_by_prefix[prefix].append(l)
    for prefix, lines_group in lessons_by_prefix.items():
        classify_and_copy_lesson(f"{lesson_title} ({prefix})", lines_group)



print("Done. All logs are in the 'logs' folder.")