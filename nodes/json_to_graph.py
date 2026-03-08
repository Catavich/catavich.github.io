import json
import argparse
from collections import deque

def extract_all_prereqs(prereq_groups):
    """Flattens the prerequisites list of lists to get all unique course IDs."""
    prereqs = set()
    for group in prereq_groups:
        for course in group:
            prereqs.add(course)
    return list(prereqs)

def build_graph(input_file, output_file, faculty=None, graph_type='3d-force'):
    with open(input_file, 'r', encoding='utf-8') as f:
        all_courses = json.load(f)

    course_dict = {str(course.get("מספר מקצוע")): course for course in all_courses if course.get("מספר מקצוע")}

    nodes_to_include = set()
    raw_edges = []

    if faculty:
        # Find all primary courses for the specific faculty
        faculty_courses = [cid for cid in course_dict if cid.startswith(faculty)]
        
        # BFS traversal to find all prerequisites recursively (up to core/root courses)
        queue = deque(faculty_courses)
        
        while queue:
            current_id = queue.popleft()
            if current_id in nodes_to_include:
                continue
                
            nodes_to_include.add(current_id)
            
            course_data = course_dict.get(current_id)
            if not course_data:
                continue
            
            prereq_groups = course_data.get("מקצועות קדם", [])
            flat_prereqs = extract_all_prereqs(prereq_groups)
            
            for prereq_id in flat_prereqs:
                raw_edges.append({"source": prereq_id, "target": current_id})
                if prereq_id not in nodes_to_include:
                    queue.append(prereq_id)
    else:
        # Include all courses if no faculty is specified
        nodes_to_include = set(course_dict.keys())
        for cid, course_data in course_dict.items():
            prereq_groups = course_data.get("מקצועות קדם", [])
            flat_prereqs = extract_all_prereqs(prereq_groups)
            for prereq_id in flat_prereqs:
                raw_edges.append({"source": prereq_id, "target": cid})

    nodes = []
    for cid in nodes_to_include:
        cdata = course_dict.get(cid, {})
        name = cdata.get("שם מקצוע", cid)
        group = cid[:2] if len(cid) >= 2 else "unknown"
        
        # 3d-force-graph expects id, name, and group is useful for coloring
        nodes.append({
            "id": cid,
            "name": name,
            "group": group,
            "val": 1 
        })

    unique_edges = []
    seen_edges = set()
    
    for edge in raw_edges:
        # Verify both ends of the edge exist in the filtered subset
        if edge["source"] in nodes_to_include and edge["target"] in nodes_to_include:
            edge_tuple = (edge["source"], edge["target"])
            if edge_tuple not in seen_edges:
                seen_edges.add(edge_tuple)
                unique_edges.append({"source": edge["source"], "target": edge["target"]})

    # Output formatting based on graph type
    if graph_type == '3d-force':
        graph_data = {"nodes": nodes, "links": unique_edges}
    else:
        # Standard generic graph format
        graph_data = {"nodes": nodes, "edges": unique_edges}

    with open(output_file, 'w', encoding='utf-8') as out_f:
        json.dump(graph_data, out_f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a JSON graph file from course data.")
    parser.add_argument("-i", "--input", required=True, help="Path to the combined courses JSON file.")
    parser.add_argument("-o", "--output", required=True, help="Path to save the output JSON graph file.")
    parser.add_argument("-f", "--faculty", help="2-digit faculty code (e.g., '23' for CS). Automatically includes prerequisite tree.", default=None)
    parser.add_argument("-t", "--type", dest="graph_type", choices=['3d-force', 'standard'], default='3d-force', help="Graph structural format (default: 3d-force).")
    
    args = parser.parse_args()
    build_graph(args.input, args.output, args.faculty, args.graph_type)
