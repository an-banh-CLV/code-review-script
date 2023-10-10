from flask import Flask, request, jsonify
import os
import lkml
import re
import subprocess
from code_review_helper import *

# Setup for Flask App
app = Flask(__name__)

subfolder_name_01 = '01_Extend_&_Refine' 
lookml_hub = 'LOOKML_one_hub'
base_path = 'C:/Users/NC/Documents/ONELooker/'

@app.route('/gitpull', methods=['POST'])
def git_pull():
    data = request.get_json()

    project_name = data.get('project_name', None)
    
    location = get_project_path(project_name)

    # Check if location directory exists
    if not os.path.exists(location):
        return jsonify(success=False, message=f"Location {location} does not exist.")
    
    # Change working directory to the specified location
    os.chdir(location)

    try:
        output = subprocess.check_output(['git', 'pull'], stderr=subprocess.STDOUT)
        return jsonify(success=True, message=output.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        return jsonify(success=False, message=e.output.decode('utf-8'))

@app.route('/runscript1', methods=['POST'])
def run_script1():
    # Extract folder paths from the POST request body
    data = request.get_json()
    project_name = data.get('project_name', None)
    folder_path_1 = get_lookml_hub_path()
    folder_path_2 = get_project_path(project_name)
    
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
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
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
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
    explore_results, test_param_results = test_03(root_folder, base_folder_name)
    
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
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
    results = test_04(root_folder, base_folder_name, subfolder_name_01)
    
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
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
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
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
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
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
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
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
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
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
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
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)

    # Ensure path is provided
    if not base_path:
        return jsonify({"error": "Folder path must be provided."}), 400

    results = test_10(root_folder)

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

@app.route('/runscript11', methods=['POST'])
def run_script11():
    # Extract folder path from the POST request body
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)

    # Ensure path is provided
    if not root_folder:
        return jsonify({"error": "Folder path must be provided."}), 400

    results = test_11(root_folder, base_folder_name)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "File Path": item[0],
        "File Name": item[1],
        "Include Statement": item[2]
    } for item in results]

    return jsonify({
        "headers": ["Folder Path", "File Name", "Include Statement"],
        "data": output_data
    })

@app.route('/runscript12', methods=['POST'])
def run_script_12():
    # Extract folder path from the POST request body
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
    results = test_12(root_folder, base_folder_name, subfolder_name_01)
    
    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "File Path": item[0],
        "File Name": item[1],
        "View Name": item[2],
        "Field Type": item[3],
        "Field Name": item[4]
    } for item in results]
    
    return jsonify({
        "headers": ["File Path", "File Name", "View Name", "Field Type", "Field Name"],
        "data": output_data
    })

@app.route('/runscript13', methods=['POST'])
def run_script_13():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
    results = test_13(root_folder, base_folder_name)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "Folder": item[0],
        "Filename": item[1],
        "View": item[2],
        "Extends from View": item[3]
    } for item in results]

    return jsonify({
        "headers": ["Folder", "Filename", "View", "Extends from View"],
        "data": output_data
    })

@app.route('/runscript14', methods=['POST'])
def run_script_14():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    
    results = test_14(root_folder, base_folder_name)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "File Path": item[0],
        "Explore Name": item[1],
        "Join Content": item[2]
    } for item in results]
    
    return jsonify({
        "headers": ["File Path", "Explore Name", "Join Content"],
        "data": output_data
    })

@app.route('/runscript15', methods=['POST'])
def run_script_15():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)
    parameter_hierarchy = ['view_name', 'group_label', 'label', 'description']
    results = []

    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.explore.lkml'):
                full_file_path = os.path.join(root, file)
                relative_folder = root.split(base_folder_name)[-1]
                if relative_folder == '':
                    folder = ''
                else:
                    folder = "/" + relative_folder.lstrip('/').replace('\\', '/') + "/"
                with open(full_file_path, 'r') as f:
                    content = f.read()

                explore_blocks = re.split(r'(?=explore:\s*[\w+]+\s*{)', content)
                for explore_block in explore_blocks:
                    if "explore:" in explore_block:
                        explore_name = re.search(r'explore:\s*([\w+]+)', explore_block)
                        if explore_name:
                            explore_name = explore_name.group(1)
                            parameters = re.findall(r'\s*(\w+):\s*', explore_block)
                            test_15(file, folder, explore_name, parameters, parameter_hierarchy, results)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "Folder": item[0],
        "Filename": item[1],
        "Explore": item[2],
        "Expected Order": item[3],
        "Current Order": item[4]
    } for item in results]

    return jsonify({
        "headers": ["Folder", "Filename", "Explore", "Expected Order", "Current Order"],
        "data": output_data
    })

@app.route('/runscript16', methods=['POST'])
def run_script_16():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)

    results = test_16(root_folder, base_folder_name)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "File Path": item[0],
        "View Name": item[1],
        "Dimension Name": item[2],
        "File Name": item[3],
        "Explore Names": item[4]
    } for item in results]

    return jsonify({
        "headers": ["File Path", "View Name", "Dimension Name", "File Name", "Explore Names"],
        "data": output_data
    })

@app.route('/runscript17', methods=['POST'])
def run_script_17():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)

    results = test_17(root_folder, base_folder_name)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "Folder": item[0],
        "View Name": item[1],
        "Dimension Name": item[2],
        "Expected Order": item[3],
        "Current Order": item[4]
    } for item in results]

    return jsonify({
        "headers": ["Folder", "View Name", "Dimension Name", "Expected Order", "Current Order"],
        "data": output_data
    })

@app.route('/runscript18', methods=['POST'])
def run_script_18():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)

    results = test_18(root_folder, base_folder_name)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "File Path": item[0],
        "View Name": item[1],
        "Dimension Name": item[2],
        "SQL Value": item[3]
    } for item in results]

    return jsonify({
        "headers": ["File Path", "View Name", "Dimension Name", "SQL Value"],
        "data": output_data
    })

@app.route('/runscript19', methods=['POST'])
def run_script_19():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)

    results = test_19(root_folder, base_folder_name)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "File Path": item[0],
        "View Name": item[1],
        "Dimension Name": item[2]
    } for item in results]

    return jsonify({
        "headers": ["File Path", "View Name", "Dimension Name"],
        "data": output_data
    })

@app.route('/runscript20', methods=['POST'])
def run_script_20():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)

    results = test_20(root_folder, base_folder_name)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "Folder": item[0],
        "File Name": item[1],
        "View Name": item[2],
        "Dimension Group": item[3]
    } for item in results]

    return jsonify({
        "headers": ["Folder", "File Name", "View Name", "Dimension Group"],
        "data": output_data
    })

@app.route('/runscript21', methods=['POST'])
def run_script_21():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)

    results = test_21(root_folder, base_folder_name)

    # Convert the results to a list of dictionaries for JSON serialization
    output_data = [{
        "Folder": item[0],
        "File Name": item[1],
        "View Name": item[2],
        "Hardcoded BQ View": item[3]
    } for item in results]

    return jsonify({
        "headers": ["Folder", "File Name", "View Name", "Hardcoded BQ View"],
        "data": output_data
    })

@app.route('/runscript22', methods=['POST'])
def run_script_22():
    data = request.get_json()
    project_name = data.get('project_name', None)
    root_folder = get_project_path(project_name)

    results = test_22(root_folder)

    # Convert the results to JSON format
    output_data = [{
        "Constant Name": item[0],
        "Parameter": item[1]
    } for item in results]

    return jsonify({
        "headers": ["Constant Name", "Parameter"],
        "data": output_data
    })

# app for fetching one-hub
@app.route('/fetchLookMLData', methods=['GET'])
def fetch_lookml_data():
    print("Endpoint hit!")
    data = []

    # Your directory path
    lookml_dir = os.path.join(os.path.expanduser('~'),'An-ONE-Looker','LOOKML_one_hub')

    for root, _, fileList in os.walk(lookml_dir):      
        for file in fileList:          
            if 'view' in file.lower():
                with open(os.path.join(root, file), 'r') as fileObj:
                    try:
                        lookml = lkml.load(fileObj)
                    except SyntaxError as e:
                        print(f"Error parsing {file}: {e}")
                        continue

                    if 'views' in lookml:
                        for view in lookml['views']:                         
                            if 'sql_table_name' in view:
                                view_name = os.path.splitext(file)[0]
                                sql_table_full = view.get('sql_table_name', '')
                                sql_table = sql_table_full.split('.')[-1].replace('`', '')                              
                                if sql_table:
                                    data.append([view_name, sql_table])
    
    # Convert the results to JSON format
    output_data = [{
        "View Name": item[0],
        "Table Name": item[1]
    } for item in data]

    return jsonify({
        "headers": ["View Name", "Table Name"],
        "data": output_data
    })

if __name__ == '__main__':
    app.run(debug=True)

