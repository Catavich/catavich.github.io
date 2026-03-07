import json
import re

def parse_prerequisites(prereqs_str):
    """
    Parses a prerequisites string of the format:
    '(A ו-B ו-C) או (D ו-A)' into [['A', 'B', 'C'], ['D', 'A']]
    """
    if not prereqs_str:
        return []
    
    # Split by ' או ' (or)
    groups = prereqs_str.split(' או ')
    parsed_groups = []
    
    for group in groups:
        # Remove parentheses
        clean_group = group.replace('(', '').replace(')', '').strip()
        if not clean_group:
            continue
        
        # Split by ' ו-' (and) or just ' ו ' using regex
        courses = [c.strip() for c in re.split(r'\s*ו-?\s*', clean_group) if c.strip()]
        
        if courses:
            parsed_groups.append(courses)
            
    return parsed_groups

def parse_exam_date(date_str):
    """
    Finds a date format like DD-MM-YYYY, DD/MM/YYYY or DD.MM.YY 
    and converts it to standard ISO YYYY-MM-DD.
    """
    if not date_str:
        return date_str
    
    # Extract date part like DD-MM-YYYY, DD/MM/YY, etc.
    match = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})', date_str)
    if match:
        day, month, year = match.groups()
        if len(year) == 2:
            year = "20" + year # Convert YY to 20YY
            
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    return date_str

def transform_single_course(course_data):
    """
    Transforms the 'general' section of a single course dictionary.
    """
    output_data = {}
    
    # Process only the 'general' section (dropping 'schedule')
    if "general" in course_data:
        for key, value in course_data["general"].items():
            if key == "מקצועות קדם":
                output_data[key] = parse_prerequisites(value)
                
            elif key == "מקצועות ללא זיכוי נוסף":
                output_data[key] = value.split() if value else []
                
            elif key in ["מועד א", "מועד ב", "מועד א'", "מועד ב'"]:
                output_data[key] = parse_exam_date(value)
                
            else:
                output_data[key] = value
                
    return output_data

def transform_course_json(data):
    """
    Takes the parsed JSON data, checks if it's a list or a single dict,
    applies transformations, and returns the new data.
    """
    # If the JSON is a list of courses (like your snippet)
    if isinstance(data, list):
        return [transform_single_course(course) for course in data]
        
    # If the JSON is a single course object
    elif isinstance(data, dict):
        return transform_single_course(data)
        
    return data

def process_file(input_filepath, output_filepath):
    """
    Reads a JSON file, transforms it, and saves it to a new file.
    """
    with open(input_filepath, 'r', encoding='utf-8') as infile:
        data = json.load(infile)
        
    transformed_data = transform_course_json(data)
    
    with open(output_filepath, 'w', encoding='utf-8') as outfile:
        # ensure_ascii=False ensures Hebrew chars save properly
        json.dump(transformed_data, outfile, ensure_ascii=False, indent=2)
        
    print(f"Success! Processed '{input_filepath}' and saved to '{output_filepath}'.")

# ==========================================
# Script Execution
# ==========================================
if __name__ == "__main__":
    # Make sure your source file is named input.json, or change this variable
    INPUT_FILE = "nodes/courses_2025_200.json"
    OUTPUT_FILE = "nodes/parsed_courses.json"
    
    try:
        process_file(INPUT_FILE, OUTPUT_FILE)
    except FileNotFoundError:
        print(f"Error: Could not find '{INPUT_FILE}'.")
    except json.JSONDecodeError:
        print(f"Error: '{INPUT_FILE}' contains invalid JSON formatting.")