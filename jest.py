import re
import llm

def parse_coverage_report(report):

    # Split the report into lines
    lines = report.strip().split("\n")

    # Remove unnecessary lines (like command output and dividers)
    lines = [line for line in lines if not re.match(r"^> test|^-+$", line.strip())]

    # Find the header row
    header_index = None
    for i, line in enumerate(lines):
        if "File" in line and "%" in line:
            header_index = i
            break
    if header_index is None:
        print("ERROR: No valid header found!")
        return []

    # Extract headers
    headers = [h.strip() for h in lines[header_index].split("|") if h.strip()]

    # Parse data rows
    data = []
    for line in lines[header_index + 3:-1]:
        row_values = [r.strip() for r in line.split("|")]
        
        # Ignore empty rows
        if not any(row_values):
            continue
        
        # If the row has fewer columns, assume it's a directory and fill missing values
        if len(row_values) < len(headers):
            row_values += [""] * (len(headers) - len(row_values))

        # Store as a dictionary
        data.append(dict(zip(headers, row_values)))

    return data

def parse_uncovered_lines(line_str):
    """Convert a string of uncovered line numbers into a list of integers."""
    line_numbers = []
    if line_str:
        parts = line_str.split(',')
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                line_numbers.extend(range(start, end + 1))
            else:
                line_numbers.append(int(part))
    return line_numbers

def read_uncovered_lines(coverage_data):
    """Read and display uncovered lines from the given coverage data."""
    for entry in coverage_data:
        file = "/home/Artefiq/code/telkom/codefixer/project_test/app/" + entry['File_path']
        line_numbers = parse_uncovered_lines(entry['Uncovered Line #s'])

        try:
            with open(file, "r") as f:
                content = f.readlines()
                uncovered_content = {ln: content[ln - 1] for ln in line_numbers if ln <= len(content)}
                
                for ln, txt in uncovered_content.items():
                    if 'Code' in entry:
                        entry['Code'] += f"{txt.strip()}\n"
                    else:
                        entry['Code'] = f"{txt.strip()}\n"
                    
        except FileNotFoundError:
            print(f"File not found: {file}")

def re_test(API_LLM_URL, API_KEY, llm_model, jest_result):
    coverage_dict = parse_coverage_report(jest_result)
    jest_path = None
    filtered_coverage = []
    for row in coverage_dict:
        if (row['File'].endswith('.js')):
            row['File_path'] = jest_path + "/" + row['File']
            if (row['Uncovered Line #s']):
                filtered_coverage.append(row)
        else:
            jest_path = row['File']

    read_uncovered_lines(filtered_coverage)
    
    for row in filtered_coverage:
        llm.fix_unit_test(API_LLM_URL, API_KEY, llm_model, row)