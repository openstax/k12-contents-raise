import os
import csv
import hashlib
import json
from bs4 import BeautifulSoup, Comment, Tag
from pathlib import Path

INPUT_DIR = '../../../grouped_html/primary_learning_activities/all'
OUTPUT_CSV = 'PLA_all_no_TEKS.csv'
LOG_FILE = 'parse_log.txt'

FIELDNAMES = [
    'data_content_id', 'filename', 'multi_step_id', 'block_index', 'rex_type',
    'question_content', 'detailed_solution',
    'Answer_A', 'Answer_B', 'Answer_C', 'Answer_D', 'Answer_E', 'Answer_F',
    'Feedback_A', 'Feedback_B', 'Feedback_C', 'Feedback_D', 'Feedback_E', 'Feedback_F',
    'correct_answer', 'background'
]

# Helpers
def log_issue(logs, message):
    logs.append(f"[WARNING] {message}")

def strip_outer_tag(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.decode_contents()

def parse_options_array(raw):
    try:
        decoded = json.loads(raw)
        return [opt.replace('\\\\', '\\') for opt in decoded]
    except:
        return []

def parse_solution_array(raw):
    try:
        return json.loads(raw)
    except:
        return []

def extract_background(soup):
    background_parts = []
    for elem in soup.contents:
        if isinstance(elem, str): continue
        if elem.name == 'div' and elem.get('class', [''])[0].startswith('os-raise-ib-'):
            if 'os-raise-ib-content' in elem.get('class', []):
                background_parts.append(str(elem))
                continue
            break
        if elem.name in ['h1', 'h2', 'h3', 'h4']:
            continue
        background_parts.append(str(elem))
    return ''.join(background_parts).strip()

def convert_options_to_list(options):
    soup = BeautifulSoup('', 'html.parser')
    ol = soup.new_tag('ol')
    for item in options:
        li = soup.new_tag('li')
        li.append(BeautifulSoup(item, 'html.parser'))
        ol.append(li)
    return str(ol)

def create_check_answer_html(solution_list):
    return f"<p>Check your answer: If you selected {', '.join(solution_list)}, that’s correct!</p>"

def clean_tooltips(soup):
    for tooltip in soup.select('.os-raise-ib-tooltip'):
        tooltip.unwrap()

def replace_desmos(soup):
    for desmos in soup.select('.os-raise-ib-desmos-gc'):
        desmos.replace_with(BeautifulSoup('<p>This requires a Desmos calculator</p>', 'html.parser'))

def extract_feedback(problem, pset_correct, pset_encourage):
    def clean_and_strip(html):
        if not html:
            return ''
        soup = BeautifulSoup(html, 'html.parser')
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        cleaned = soup.decode_contents().strip()
        return cleaned if cleaned else ''

    correct = problem.select_one('.os-raise-ib-pset-correct-response')
    encourage = problem.select_one('.os-raise-ib-pset-encourage-response')

    correct_html = correct.decode_contents().strip() if correct else pset_correct
    encourage_html = encourage.decode_contents().strip() if encourage else pset_encourage

    return clean_and_strip(correct_html), clean_and_strip(encourage_html)

def strip_surrounding_br_tags(html_str):
    soup = BeautifulSoup(html_str, 'html.parser')
    while soup.contents and soup.contents[0].name == 'br':
        soup.contents[0].decompose()
    while soup.contents and soup.contents[-1].name == 'br':
        soup.contents[-1].decompose()
    return str(soup.prettify())

def process_interactive_block(block, filename, multi_step_id, block_index_start, background, lead_in_buffer, logs):
    def clean_html(html):
        soup = BeautifulSoup(html, 'html.parser')
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        while soup.contents and soup.contents[0].name == 'br':
            soup.contents[0].decompose()
        while soup.contents and soup.contents[-1].name == 'br':
            soup.contents[-1].decompose()
        return soup.decode_contents().strip()

    rows = []
    lead_in_html = clean_html(''.join(lead_in_buffer).strip())

    if 'os-raise-ib-pset' in block.get('class', []):
        pset_correct_elem = block.select_one('.os-raise-ib-pset-correct-response')
        pset_encourage_elem = block.select_one('.os-raise-ib-pset-encourage-response')
        pset_correct = clean_html(pset_correct_elem.decode_contents()) if pset_correct_elem else ''
        pset_encourage = clean_html(pset_encourage_elem.decode_contents()) if pset_encourage_elem else ''

        for i, problem in enumerate(block.select('.os-raise-ib-pset-problem')):
            row = {key: '' for key in FIELDNAMES}
            row.update({
                'filename': filename,
                'multi_step_id': multi_step_id,
                'block_index': block_index_start + i,
                'rex_type': '',
                'background': background,
            })

            data_id = problem.get('data-content-id') or f"{Path(filename).stem}__block{block_index_start + i}"
            if not problem.get('data-content-id'):
                log_issue(logs, f"Missing data-content-id in file {filename}, block {block_index_start + i}")
            row['data_content_id'] = data_id

            prob_type = problem.get('data-problem-type', '').lower()
            row['rex_type'] = 'open_ended' if prob_type in ['input', 'multiselect'] else 'multiple_choice'

            content_html = problem.select_one('.os-raise-ib-pset-problem-content')
            question = content_html.decode_contents().strip() if content_html else ''

            if prob_type == 'multiselect':
                opts = parse_options_array(problem.get('data-solution-options', '[]'))
                question += convert_options_to_list(opts)
                sol = parse_solution_array(problem.get('data-solution', '[]'))
                row['detailed_solution'] = create_check_answer_html(sol)

            elif prob_type in ['multiplechoice', 'dropdown']:
                opts = parse_options_array(problem.get('data-solution-options', '[]'))
                sol = problem.get('data-solution')
                try:
                    idx = opts.index(sol)
                    row['correct_answer'] = chr(65 + idx)
                except:
                    log_issue(logs, f"data-solution does not match options in {filename}, block {block_index_start + i}")
                    row['correct_answer'] = 'NEED ANSWER'

                for j, opt in enumerate(opts[:6]):
                    row[f'Answer_{chr(65+j)}'] = opt

                correct_html = problem.select_one('.os-raise-ib-pset-correct-response')
                encourage_html = problem.select_one('.os-raise-ib-pset-encourage-response')

                correct_clean = clean_html(correct_html.decode_contents()) if correct_html else pset_correct
                encourage_clean = clean_html(encourage_html.decode_contents()) if encourage_html else pset_encourage

                for j in range(len(opts[:6])):
                    key = chr(65+j)
                    row[f'Feedback_{key}'] = correct_clean if key == row['correct_answer'] else encourage_clean

            elif prob_type == 'input':
                solution = problem.get('data-solution')
                row['detailed_solution'] = f"<p>Check your answer with the solution: {solution}</p>"

            row['question_content'] = clean_html(f"{lead_in_html}<br>{question}")
            rows.append(row)

    elif 'os-raise-ib-cta' in block.get('class', []):
        row = {key: '' for key in FIELDNAMES}
        row.update({
            'filename': filename,
            'multi_step_id': multi_step_id,
            'block_index': block_index_start,
            'rex_type': 'open_ended',
            'background': background,
        })
        row['data_content_id'] = block.get('data-content-id') or f"{Path(filename).stem}__block{block_index_start}"

        content = block.select_one('.os-raise-ib-cta-content')
        prompt = block.select_one('.os-raise-ib-cta-prompt')
        content_html = content.decode_contents().strip() if content else ''
        prompt_html = prompt.decode_contents().strip() if prompt else ''

        row['question_content'] = clean_html(f"{lead_in_html}<br>{content_html}<br>{prompt_html}")

        fire_event = block.get('data-fire-event')
        if fire_event:
            matched_content = block.find_all_next('div', class_='os-raise-ib-content', attrs={'data-wait-for-event': fire_event})
            row['detailed_solution'] = ''.join([c.decode_contents() for c in matched_content])

        rows.append(row)

    elif 'os-raise-ib-input' in block.get('class', []):
        row = {key: '' for key in FIELDNAMES}
        row.update({
            'filename': filename,
            'multi_step_id': multi_step_id,
            'block_index': block_index_start,
            'rex_type': 'open_ended',
            'background': background,
        })
        row['data_content_id'] = block.get('data-content-id') or f"{Path(filename).stem}__block{block_index_start}"

        content = block.select_one('.os-raise-ib-input-content')
        prompt = block.select_one('.os-raise-ib-input-prompt')
        ack = block.select_one('.os-raise-ib-input-ack')

        content_html = content.decode_contents().strip() if content else ''
        prompt_html = prompt.decode_contents().strip() if prompt else ''
        ack_html = ack.decode_contents().strip() if ack else ''

        row['question_content'] = clean_html(f"{lead_in_html}<br>{content_html}<br>{prompt_html}")
        row['detailed_solution'] = clean_html(ack_html)

        rows.append(row)

    return rows

def split_by_ready_for_more(soup):
    rfm_blocks = [
        tag for tag in soup.find_all('div', class_='os-raise-ib-cta')
        if 'are you ready for more' in tag.get('data-button-text', '').lower()
    ]

    if len(rfm_blocks) > 1:
        return 'MULTIPLE_RFM', None, None
    elif len(rfm_blocks) == 0:
        return 'NO_RFM', soup, None

    split_block = rfm_blocks[0]
    before = BeautifulSoup('', 'html.parser')
    after = BeautifulSoup('', 'html.parser')
    seen_split = False

    for el in soup.contents:
        if not isinstance(el, Tag):
            continue
        if el is split_block:
            seen_split = True
            continue  # skip the RFM block itself
        if seen_split:
            after.append(el)
        else:
            before.append(el)

    return 'SPLIT', before, after

def has_interactive_blocks(soup):
    if not soup:
        return False
    for tag in soup.find_all(True):
        classes = tag.get('class', [])
        if any(cls in classes for cls in ['os-raise-ib-pset', 'os-raise-ib-input', 'os-raise-ib-cta']):
            return True
    return False

def process_section(soup, filename, multi_step_id, logs):
    rows = []
    block_index = 0
    lead_in_buffer = []
    background_parts = []
    found_first_interactive = False

    for elem in soup.contents:
        if isinstance(elem, str):
            continue

        is_interactive = elem.name == 'div' and any(cls in elem.get('class', []) for cls in [
            'os-raise-ib-pset', 'os-raise-ib-input', 'os-raise-ib-cta']
        )

        if not found_first_interactive:
            if is_interactive:
                background = strip_surrounding_br_tags(''.join(background_parts).strip())
                rows_from_block = process_interactive_block(
                    elem, filename, multi_step_id, block_index, background, lead_in_buffer, logs)
                rows.extend(rows_from_block)
                block_index += len(rows_from_block)
                lead_in_buffer.clear()
            else:
                if elem.name not in ['h1', 'h2', 'h3', 'h4']:
                    background_parts.append(str(elem))
        else:
            if is_interactive:
                rows_from_block = process_interactive_block(
                    elem, filename, multi_step_id, block_index, background, lead_in_buffer, logs)
                rows.extend(rows_from_block)
                block_index += len(rows_from_block)
                lead_in_buffer.clear()
            else:
                lead_in_buffer.append(str(elem))
    return rows

def main():
    all_rows = []
    logs = []
    multi_step_counter = 1

    for file in sorted(Path(INPUT_DIR).glob('*.html')):
        with open(file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        filename = file.name
        status, before_soup, after_soup = split_by_ready_for_more(soup)

        if status == 'MULTIPLE_RFM':
            log_issue(logs, f"Multiple 'Are you ready for more?' CTA blocks found in file {filename}. Skipping.")
            continue

        if status == 'NO_RFM':
            if has_interactive_blocks(before_soup):
                multi_step_id = f"PLA_{multi_step_counter}"
                rows = process_section(before_soup, filename, multi_step_id, logs)
                all_rows.extend(rows)
                multi_step_counter += 1
            else:
                log_issue(logs, f"No interactive blocks in file {filename}. Skipping.")
            continue

        if has_interactive_blocks(before_soup):
            multi_step_id = f"PLA_{multi_step_counter}"
            rows = process_section(before_soup, filename, multi_step_id, logs)
            all_rows.extend(rows)
            multi_step_counter += 1

        if has_interactive_blocks(after_soup):
            multi_step_id = f"PLA_{multi_step_counter}"
            rows = process_section(after_soup, filename, multi_step_id, logs)
            all_rows.extend(rows)
            multi_step_counter += 1
        else:
            log_issue(logs, f"No interactive blocks found after 'Are you ready for more?' in {filename}. Skipping second section.")

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    if logs:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(logs))
    print(f"✅ Finished. Parsed {len(all_rows)} rows across {multi_step_counter - 1} multi-step entries.")

if __name__ == "__main__":
    main()
