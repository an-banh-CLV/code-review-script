from flask import Flask, request, jsonify
import os
import lkml
import pandas as pd
import re

# Functions for Test 1
def extract_all_view_names(file_path):
    view_names = set()
    
    with open(file_path, 'r') as fileObj:
        try:
            lookml = lkml.load(fileObj)
        except SyntaxError as e:
            print(f"Error parsing {file_path}: {e}")
            return view_names

        if 'views' in lookml:
            for view in lookml['views']:
                if 'name' in view:
                    view_names.add(view['name'])

    return view_names

def extract_relevant_views(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    views_to_check = []
    for view in parsed.get('views', []):
        if 'extends' in view:
            views_to_check.extend(view['extends'])
        if view['name'].startswith('+'):
            views_to_check.append(view['name'].lstrip('+'))
    
    return views_to_check

def test_01(folder_path_1, folder_path_2, subfolder_name):
    view_names_from_path_1 = set()  # Using set for O(1) lookups
    for foldername, _, filenames in os.walk(folder_path_1):
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                view_names_from_path_1.update(extract_all_view_names(file_path))

    results = []
    target_folder_2 = os.path.join(folder_path_2, subfolder_name)
    views_from_path_2_to_check = set()  # Use a set to store views from path_2 to avoid duplicates
    for foldername, _, filenames in os.walk(target_folder_2):
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                views_from_path_2 = extract_relevant_views(file_path)
                views_from_path_2_to_check.update(views_from_path_2)
                for view_name in views_from_path_2:
                    if view_name not in view_names_from_path_1:
                        results.append((foldername, filename, view_name))
    return results

# Functions for Test 2
def extract_views_without_derived_table(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    views_without_derived_table = []
    for view in parsed.get('views', []):
        if 'derived_table' not in view:
            views_without_derived_table.append(view['name'])
    
    return views_without_derived_table

def test_02(root_folder, base_folder_name):
    results = []

    # Focus on the desired sub-folder
    target_folder = os.path.join(root_folder, "03_Spoke_Marts", "01_Common_Marts")
    
    base_path_parts = os.path.normpath(target_folder).split(os.sep)
    base_index = base_path_parts.index(base_folder_name)
    
    for foldername, subfolders, filenames in os.walk(target_folder):
        path_parts = os.path.normpath(foldername).split(os.sep)
        relative_path = os.sep.join(path_parts[base_index:])
        
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(relative_path, filename)
                
                # Check view names inside the file
                full_path = os.path.join(foldername, filename)
                views = extract_views_without_derived_table(full_path)
                for view_name in views:
                    results.append((file_path, filename, view_name))
    
    return results

# Functions for Test 3
def extract_test_param_files(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    if "test:" in content:
        return True
    return False

def test_03(root_folder, base_folder_name):
    relevant_fields = []
    explore_files = []
    test_param_files = []

    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, _, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        for filename in filenames:
            if filename.endswith('.explore.lkml'):
                explore_files.append((relative_path, filename))
            
            if filename.endswith('.lkml') and extract_test_param_files(os.path.join(foldername, filename)):
                test_param_files.append((relative_path, filename))
    
    return explore_files, test_param_files  

# Functions for Test 4
def test_04(root_folder, base_folder_name, target_subfolder):
    results = []
    
    # Add the target subfolder to the root folder path
    full_folder_path = os.path.join(root_folder, target_subfolder)
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_index = base_path_parts.index(base_folder_name)
    
    for foldername, subfolders, filenames in os.walk(full_folder_path):
        path_parts = os.path.normpath(foldername).split(os.sep)
        relative_path = os.sep.join(path_parts[base_index:])
        
        for filename in filenames:
            if filename.endswith('.view.lkml') and not filename.endswith('_r.view.lkml'):
                file_path = os.path.join(relative_path, filename)
                results.append((file_path, filename))
    
    return results

# Functions for Test 5
def test_05(root_folder, base_folder_name):
    files_outside_models = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        if '02_Models' not in relative_path:
            for filename in filenames:
                if filename.endswith('.explore.lkml'):
                    files_outside_models.append((relative_path, filename))
    
    return files_outside_models

# Functions for Test 6
def extract_parameters(file_path):
    # Define parameters and their expected values
    expected_params = {
        "case_sensitive": "no",
        "connection": ["onedw", "onedw_new"],
        "fiscal_month_offset": "3",
        "week_start_day": "sunday"
    }
    
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)

    missing_or_wrong = []

    for param, expected_val in expected_params.items():
        value = parsed.get(param)
        if not value:
            missing_or_wrong.append(param)
        elif isinstance(expected_val, list):
            if value not in expected_val:
                missing_or_wrong.append(param)
        elif value != expected_val:
            missing_or_wrong.append(param)
    
    return missing_or_wrong

def test_06(root_folder, base_folder_name):
    target_files = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        if "02_Models" in relative_path:
            for filename in filenames:
                if filename.endswith('.model.lkml'):
                    file_path = os.path.join(foldername, filename)
                    issues = extract_parameters(file_path)
                    if issues:
                        target_files.append((relative_path, filename, ", ".join(issues)))
    
    return target_files

# Functions for Test 07

def extract_includes(file_path):
    with open(file_path, 'r') as f:
        content = f.readlines()

    include_statements = [line.strip() for line in content if line.startswith('include:') and '/explore.lkml' in line]
    
    return include_statements

def test_07(root_folder, base_folder_name):
    target_files = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        if "02_Models" in relative_path:
            for filename in filenames:
                if filename.endswith('.model.lkml'):
                    file_path = os.path.join(foldername, filename)
                    includes = extract_includes(file_path)
                    for include in includes:
                        target_files.append((relative_path, filename, include))
    
    return target_files

# Functions for Test 08
def test_08(root_folder, base_folder_name):
    results = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_index = base_path_parts.index(base_folder_name)
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        path_parts = os.path.normpath(foldername).split(os.sep)
        relative_path = os.sep.join(path_parts[base_index:])
        
        # Only consider folders starting with "02_" and ending with "_Marts"
        if path_parts[-1].startswith('02_') and path_parts[-1].endswith('_Marts'):
            results.append((relative_path, path_parts[-1]))  # Adding folder name to the results
    
    return results

# Functions for Test 09
def extract_view_names(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    return [view['name'] for view in parsed.get('views', [])]

def test_09(root_folder, base_folder_name):
    results = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_index = base_path_parts.index(base_folder_name)
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        path_parts = os.path.normpath(foldername).split(os.sep)
        relative_path = os.sep.join(path_parts[base_index:])
        
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(relative_path, filename)
                
                # Check the filename first
                if filename.endswith('_v.view.lkml'):
                    results.append((file_path, filename, 'N/A'))
                
                # Check view names inside the file
                full_path = os.path.join(foldername, filename)
                views = extract_view_names(full_path)
                for view_name in views:
                    if view_name.endswith('_v'):
                        results.append((file_path, filename, view_name))
    
    return results

# Functions for Test 10
def check_parameter_order(parameters, parameter_hierarchy):
    """Checks the order of parameters against the hierarchy and returns the order as a string."""
    correct_order = True
    last_index = -1
    filtered_params = [param for param in parameters if param in parameter_hierarchy]
    for param in filtered_params:
        param_index = parameter_hierarchy.index(param)
        if param_index < last_index:
            correct_order = False
            break
        last_index = param_index


    if correct_order:
        return None, None


    parameter_order_str = ', '.join([param for param in parameter_hierarchy if param in filtered_params])
    current_order_str = ', '.join([param for param in filtered_params])
    return parameter_order_str, current_order_str

def get_explore_names(base_path, view_name):
    """Returns a list of explore names where the term 'view_name.' is found in the 'fields' parameter."""
    explore_names = []


    for root, _, fileList in os.walk(base_path):
        for file in fileList:
            if file.endswith('.explore.lkml'):
                with open(os.path.join(root, file), 'r') as fileObj:
                    content = fileObj.read()
                   
                    # Use regex to find content inside square brackets after "fields:"
                    match = re.search(r'fields:\s*\[([^\]]+)\]', content)
                    if match:
                        fields_content = match.group(1)
                        # check if the term "view_name." is in the extracted content
                        if f"{view_name}." in fields_content:
                            # extract the explore name from the file name
                            explore_name = file.replace('.explore.lkml', '')
                            if explore_name not in explore_names:
                                explore_names.append(explore_name)


    # Return the explore names separated by a comma
    return ', '.join(explore_names)

def test_10(base_path):
    parameter_hierarchy = ['hidden', 'view_label', 'group_label', 'group_item_label', 'label', 'type','description','sql_distinct_key','sql']
    results = []

    for root, _, fileList in os.walk(base_path):
        for file in fileList:
            if 'view.lkml' in file.lower():
                with open(os.path.join(root, file), 'r') as fileObj:
                    lookml = lkml.load(fileObj)
                    if 'views' in lookml:
                        for view in lookml['views']:
                            original_view_name = view['name']
                            stripped_view_name = original_view_name.lstrip('+')
                            view_name = '="{}"'.format(view['name']) if view['name'].startswith('+') else view['name']
                            matched_explores = get_explore_names(base_path, stripped_view_name)
                            for kind in ['dimensions', 'measures']:
                                for item in view.get(kind, []):
                                    parameters = list(item.keys())
                                    expected_order, current_order = check_parameter_order(parameters, parameter_hierarchy)
                                    if expected_order and current_order:
                                        relative_path = os.path.relpath(root, base_path)
                                        results.append((relative_path, file, view_name, item.get('name', ''), matched_explores, kind, expected_order, current_order))
    
    return results

# Setup for Flask App
app = Flask(__name__)

subfolder_name_01 = '01_Extend_&_Refine' 

@app.route('/runscript1', methods=['POST'])
def run_script1():
    # Extract folder paths from the POST request body
    data = request.get_json()
    folder_path_1 = data.get('folder_path_hub')
    folder_path_2 = data.get('folder_path_spoke')
    
    # Ensure paths are provided
    if not folder_path_1 or not folder_path_2:
        return jsonify({"error": "Both folder paths must be provided."}), 400

    results = test_01(folder_path_1, folder_path_2, subfolder_name_01)
    
    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{"Folder Path": item[0], "File Name": item[1], "View Name": item[2]} for item in results]
    
    return jsonify({
    "headers": ["Folder Path", "File Name", "View Name"],
    "data": output_data
    })


@app.route('/runscript2', methods=['POST'])
def run_script2():
    # Extract folder path from the POST request body
    data = request.get_json()
    root_folder = data.get('folder_path_spoke')
    base_folder_name = data.get('base_folder')
    
    # Ensure path is provided
    if not root_folder:
        return jsonify({"error": "Folder path must be provided."}), 400

    results = test_02(root_folder, base_folder_name)
    
    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{"File Path": item[0], "File Name": item[1], "View Name": item[2]} for item in results]
    
    return jsonify({
    "headers": ["File Path", "File Name", "View Name"],
    "data": output_data
    })

@app.route('/runscript3', methods=['POST'])
def run_script_3():
    # Extract folder path from the POST request body
    data = request.get_json()
    folder_path = data.get('folder_path_spoke')
    base_folder_name = data.get('base_folder')
    explore_results, test_param_results = test_03(folder_path, base_folder_name)
    
    headers = ["Folder Path", "File Name"]
    results = []
    
    if len(explore_results) != len(test_param_results):
        results = explore_results + test_param_results

    return jsonify({
        "headers": headers,
        "data": results
    })

@app.route('/runscript4', methods=['POST'])
def run_script_4():
    # Extract folder path from the POST request body
    data = request.get_json()
    folder_path = data.get('folder_path_spoke')
    base_folder_name = data.get('base_folder')
    
    results = test_04(folder_path, base_folder_name, subfolder_name_01)
    
    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{"File Path": item[0], "File Name": item[1]} for item in results]
    
    return jsonify({
        "headers": ["File Path", "File Name"],
        "data": output_data
    })

@app.route('/runscript5', methods=['POST'])
def run_script5():
    # Extract folder path from the POST request body
    data = request.get_json()
    root_folder = data.get('folder_path_spoke')
    base_folder_name = data.get('base_folder')
    
    # Ensure path is provided
    if not root_folder or not base_folder_name:
        return jsonify({"error": "Folder path and base folder name must be provided."}), 400
    
    results = test_05(root_folder, base_folder_name)
    
    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{"Folder Path": item[0], "File Name": item[1]} for item in results]
        
    return jsonify({
        "headers": ["File Path", "File Name"],
        "data": output_data
        })

@app.route('/runscript6', methods=['POST'])
def run_script6():
    # Extract folder path from the POST request body
    data = request.get_json()
    root_folder = data.get('folder_path_spoke')
    base_folder_name = data.get('base_folder')
    
    # Ensure path is provided
    if not root_folder or not base_folder_name:
        return jsonify({"error": "Folder path and base folder name must be provided."}), 400
    
    results = test_06(root_folder, base_folder_name)
    
    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{"File Path": item[0], "File Name": item[1], "Issues": item[2]} for item in results]
        
    return jsonify({
        "headers": ["File Path", "File Name", "Issues"],
        "data": output_data
        })

@app.route('/runscript7', methods=['POST'])
def run_script7():
    # Extract folder path from the POST request body
    data = request.get_json()
    root_folder = data.get('folder_path_spoke')
    base_folder_name = data.get('base_folder')
    
    # Ensure path is provided
    if not root_folder or not base_folder_name:
        return jsonify({"error": "Folder path and base folder name must be provided."}), 400
    
    results = test_07(root_folder, base_folder_name)
    
    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{"File Path": item[0], "File Name": item[1], "Include Statement": item[2]} for item in results]
        
    return jsonify({
        "headers": ["File Path", "File Name", "Include Statement"],
        "data": output_data
        })

@app.route('/runscript8', methods=['POST'])
def run_script8():
    # Extract folder path from the POST request body
    data = request.get_json()
    root_folder = data.get('folder_path_spoke')
    base_folder_name = data.get('base_folder')
    
    # Ensure path is provided
    if not root_folder or not base_folder_name:
        return jsonify({"error": "Folder path and base folder name must be provided."}), 400
    
    results = test_08(root_folder, base_folder_name)
    
    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{"Folder Path": item[0], "Folder Name": item[1]} for item in results]
        
    return jsonify({
        "headers": ["Folder Path", "Folder Name"],
        "data": output_data
        })

@app.route('/runscript9', methods=['POST'])
def run_script9():
    # Extract folder path from the POST request body
    data = request.get_json()
    root_folder = data.get('folder_path_spoke')
    base_folder_name = data.get('base_folder')
    
    # Ensure path is provided
    if not root_folder or not base_folder_name:
        return jsonify({"error": "Folder path and base folder name must be provided."}), 400
    
    results = test_09(root_folder, base_folder_name)
    
    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{"File Path": item[0], "File Name": item[1], "View Name": item[2]} for item in results]
        
    return jsonify({
        "headers": ["File Path", "File Name", "View Name"],
        "data": output_data
        })

@app.route('/runscript10', methods=['POST'])
def run_script10():
    # Extract folder path from the POST request body
    data = request.get_json()
    base_path = data.get('folder_path_spoke')

    # Ensure path is provided
    if not base_path:
        return jsonify({"error": "Folder path must be provided."}), 400

    results = test_10(base_path)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "Folder Path": item[0],
        "File Name": item[1],
        "View Name": item[2],
        "Dimension/Measure Name": item[3],
        "Matched Explores": item[4],
        "Type": item[5],
        "Expected Order": item[6],
        "Current Order": item[7]
    } for item in results]

    return jsonify({
        "headers": ["Folder Path", "File Name", "View Name", "Dimension/Measure Name", "Matched Explores", "Type", "Expected Order", "Current Order"],
        "data": output_data
    })

if __name__ == '__main__':
    app.run(debug=True)

