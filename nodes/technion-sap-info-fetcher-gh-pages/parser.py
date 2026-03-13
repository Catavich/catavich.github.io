import json
import re
import os
from pathlib import Path

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
        return [transform_single_course(data)] # Always return a list for easier iteration
        
    return []

def process_directory(input_dir, output_filepath):
    """
    Scans directory for matching JSON files, transforms the courses, 
    combines them, and adds a field for the semesters they were taught.
    """
    dir_path = Path(input_dir)
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: Directory '{input_dir}' not found.")
        return

    # Regex matches exactly 'courses_YYYY_SEM.json'
    # Fails on '_unfilterred' or '.js'
    file_pattern = re.compile(r'^courses_(\d{4}_\d+)\.json$')
    
    combined_courses = {}
    course_semesters = {}

    for filepath in dir_path.iterdir():
        if not filepath.is_file():
            continue
            
        match = file_pattern.match(filepath.name)
        if not match:
            continue
            
        semester_tag = match.group(1) # Extracts "2025_201"
        
        with open(filepath, 'r', encoding='utf-8') as infile:
            try:
                data = json.load(infile)
            except json.JSONDecodeError:
                print(f"Error: '{filepath.name}' contains invalid JSON formatting. Skipping.")
                continue
                
        transformed_data = transform_course_json(data)
        
        for course in transformed_data:
            course_id = course.get("מספר מקצוע")
            if not course_id:
                continue
                
            # If we haven't seen this course yet, add it to our combined dictionary
            if course_id not in combined_courses:
                combined_courses[course_id] = course
                course_semesters[course_id] = set()
                
            # Add the semester tag to this course's set
            course_semesters[course_id].add(semester_tag)

    # Attach the sorted semesters to each course and prepare final list
    final_list = []
    for course_id, course_data in combined_courses.items():
        course_data['סמסטרים בהם הועבר'] = sorted(list(course_semesters[course_id]))
        final_list.append(course_data)

    with open(output_filepath, 'w', encoding='utf-8') as outfile:
        json.dump(final_list, outfile, ensure_ascii=False, indent=2)
        
    print(f"Success! Processed directory '{input_dir}' and saved combined data to '{output_filepath}'.")

# ==========================================
# Script Execution
# ==========================================
if __name__ == "__main__":
    INPUT_DIR = r"C:\Users\Dell\alias\catavich.github.io\nodes\technion-sap-info-fetcher-gh-pages"
    OUTPUT_FILE = os.path.join(INPUT_DIR, "combined_parsed_courses.json")
    
    process_directory(INPUT_DIR, OUTPUT_FILE)