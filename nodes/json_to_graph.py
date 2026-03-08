import json
import argparse
import os
from typing import List, Dict, Any

def transform_to_force_graph(input_filepath: str, output_filepath: str) -> None:
    """
    Reads a JSON file of courses and converts it to a graph data structure
    for the 3d-force-graph library. Focuses on the Computer Science faculty.
    """
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data: List[Dict[str, Any]] = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find input file at '{os.path.abspath(input_filepath)}'")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{input_filepath}' contains invalid JSON.")
        return

    nodes_dict: Dict[str, Dict[str, Any]] = {}
    links: List[Dict[str, str]] = []
    
    target_faculty = "הפקולטה למדעי המחשב"

    # First pass: Create nodes for all Computer Science courses
    for course in data:
        #if course.get("פקולטה") == target_faculty:
            course_id = course["מספר מקצוע"]
            nodes_dict[course_id] = {
                "id": course_id,
                "name": course.get("שם מקצוע", ""),
                "faculty": course.get("פקולטה", ""),
                "group": target_faculty, # Useful for coloring nodes in the library
                "points": course.get("נקודות", "0")
            }

    # Second pass: Create links and find prerequisite courses from other faculties
    for course in data:
        target_id = course["מספר מקצוע"]
        
        # We only check courses that are in Computer Science as targets
        if target_id in nodes_dict:
            prereqs = course.get("מקצועות קדם", [])
            
            # Flatten the AND/OR array to get all unique course IDs
            unique_prereq_ids = set()
            for or_group in prereqs:
                for prereq_id in or_group:
                    unique_prereq_ids.add(prereq_id)
            
            for prereq_id in unique_prereq_ids:
                # Add an edge from the prerequisite to the course
                links.append({
                    "source": prereq_id,
                    "target": target_id
                })
                
                # If the prerequisite is not yet in the nodes (e.g., a Math course), add it
                if prereq_id not in nodes_dict:
                    # Find prerequisite details in the original data
                    ext_course = next((c for c in data if c["מספר מקצוע"] == prereq_id), None)
                    
                    if ext_course:
                        nodes_dict[prereq_id] = {
                            "id": prereq_id,
                            "name": ext_course.get("שם מקצוע", ""),
                            "faculty": ext_course.get("פקולטה", "Other"),
                            "group": ext_course.get("פקולטה", "Other"),
                            "points": ext_course.get("נקודות", "0")
                        }
                    else:
                        # Edge case: Prerequisite course that doesn't appear in the dataset at all
                        nodes_dict[prereq_id] = {
                            "id": prereq_id,
                            "name": "Unknown",
                            "faculty": "Unknown",
                            "group": "Unknown",
                            "points": "0"
                        }

    # Assemble the final structure required by the library
    graph_data = {
        "nodes": list(nodes_dict.values()),
        "links": links
    }

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
        print(f"Conversion complete. Created {len(graph_data['nodes'])} nodes and {len(graph_data['links'])} links.")
        print(f"Output saved to: {os.path.abspath(output_filepath)}")
    except Exception as e:
        print(f"Error creating output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converts a courses JSON file to a graph dataset for 3d-force-graph")
    parser.add_argument("-i", "--input", default="input_courses.json", help="Path to the input courses JSON file (default: input_courses.json)")
    parser.add_argument("-o", "--output", default="output_graph.json", help="Path to the output file (default: output_graph.json)")
    
    args = parser.parse_args()
    
    transform_to_force_graph(args.input, args.output)