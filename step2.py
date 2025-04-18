from bs4 import BeautifulSoup
import re

MATCH_OUTCOMES = [
    "Time Limit Draw",
    "Double Count Out",
    "No Contest",
    "Double DQ",
    "Draw"
]

def remove_tags(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all(['a', 'span', 'div']):
        tag.replace_with(tag.text)
    return str(soup)

def normalize_text(text):
    text = text.replace("defeats", " defeat ")
    text = text.replace(" defeat ", "\ndefeat\n")

    if "defeat" not in text:
        text = text.replace("vs.", "\nvs.\n")

    return text

def format_time_and_opponent(text):
    match = re.search(r"\((\d{1,2}:\d{2})\)", text)
    if match:
        time_str = match.group(0)  
        text = text.replace(time_str, "").strip()  
        text = f"{text}\n{time_str}"
    else:
        # If no time is found, add "Time Not Provided"
        text = f"{text}\nTime Not Provided"  
    return text

def replace_vs_with_outcome(text, full_record):
    for outcome in MATCH_OUTCOMES:
        if outcome in full_record:
            return text.replace("vs.", f"\n{outcome}\n")
    return text

def replace_amp(text):
    return text.replace("&amp;", " & ")

def handle_dq_case(lines):
    if len(lines) >= 3:
        if "by DQ" in lines[2]:
            lines[1] = "defeat by DQ"  
            lines[2] = lines[2].replace("by DQ", "").strip()
        elif "by referee's decision" in lines[2]:
            lines[1] = "defeat by referee's decision"
            lines[2] = lines[2].replace("by referee's decision", "").strip()  
        elif "by Count Out" in lines[2]:
            lines[1] = "defeat by count out"
            lines[2] = lines[2].replace("by Count Out", "").strip()
    return lines

def extract_title_change(lines):
    if len(lines) >= 3 and "-TITLE CHANGE !!!" in lines[2]:
        lines[2] = lines[2].replace("-TITLE CHANGE !!!", "").strip()
        lines.append("TITLE CHANGE !!!")
    return lines

def clean_match_outcome_from_line_3(lines):
    if len(lines) >= 3:
        for outcome in MATCH_OUTCOMES:
            # Check if the outcome is in the third line and remove it
            if f"- {outcome}" in lines[2]:
                lines[2] = lines[2].replace(f"- {outcome}", "").strip()
                # Move the outcome to the second line if it's not already there
                if outcome not in lines[1]:
                    lines.insert(1, outcome)
            elif outcome in lines[2]:
                lines[2] = lines[2].replace(outcome, "").strip()
                # Move the outcome to the second line if it's not already there
                if outcome not in lines[1]:
                    lines.insert(1, outcome)
    return lines

def remove_time_limit_draw(text):
    """Remove '- Time Limit Draw' from the text."""
    return text.replace("- Time Limit Draw", "").strip()

def remove_double_count_out(text):
    return text.replace("- Double Count Out", "").strip()

def remove_no_contest(text):
    return text.replace("- No Contest", "").strip()

def remove_double_dq(text):
    return text.replace("- Double DQ", "").strip()

def remove_draw(text):
    return text.replace("- Draw", "").strip()


def remove_empty_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    with open(file_path, 'w', encoding='utf-8') as outfile:
        outfile.writelines(line for line in lines if line.strip())

def reformat_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        content = infile.read()
        records = content.split('--------------------------------------------------')

        for record in records:
            if not record.strip():
                continue

            match_card = ''
            match_event_line = ''

            match_card_start = record.find('<span class="MatchCard">')
            match_card_end = record.find('</span>', match_card_start) + len('</span>')
            if match_card_start != -1 and match_card_end != -1:
                match_card = record[match_card_start:match_card_end].replace('\n', '').strip()
                match_card = remove_tags(match_card)
                match_card = normalize_text(match_card)
                match_card = replace_amp(match_card)

            match_event_start = record.find('<div class="MatchEventLine">')
            match_event_end = record.find('</div>', match_event_start) + len('</div>')
            if match_event_start != -1 and match_event_end != -1:
                match_event_line = record[match_event_start:match_event_end].replace('\n', '').strip()
                match_event_line = remove_tags(match_event_line)
                match_event_line = replace_amp(match_event_line)

                if "@" in match_event_line:
                    event_parts = match_event_line.split("@", 1)
                else:
                    event_parts = match_event_line.split("-", 1)

                event_name = event_parts[0].strip()
                location = event_parts[1].strip() if len(event_parts) > 1 else ""

            match_card = format_time_and_opponent(match_card)
            match_card = replace_vs_with_outcome(match_card, record)

            # Remove "- Time Limit Draw" and similar outcomes
            match_card = remove_time_limit_draw(match_card)
            match_card = remove_double_count_out(match_card)
            match_card = remove_no_contest(match_card)
            match_card = remove_double_dq(match_card)
            match_card = remove_draw(match_card)

            # Remove "by referee's decision" from the match card

            match_card_lines = match_card.split("\n")
            match_card_lines = handle_dq_case(match_card_lines)  # Handle DQ and referee's decision
            match_card_lines = clean_match_outcome_from_line_3(match_card_lines)
            match_card_lines.append(event_name)
            if location:
                match_card_lines.append(location)

            match_card_lines = extract_title_change(match_card_lines)

            outfile.write("\n".join(match_card_lines) + "\n")
            outfile.write("--------------------------------------------------\n")

    remove_empty_lines(output_file)

# Example usage
input_file = './data/extracted_html.txt'
output_file = './data/output.txt'
reformat_file(input_file, output_file)