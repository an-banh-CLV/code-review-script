import os
import lkml
import re
import pandas as pd

subfolder_name_01 = '01_Extend_&_Refine' 
lookml_hub = 'LOOKML_one_hub'
base_path = '/home/looker/An-ONE-Looker/'
base_folder_name = 'An-ONE-Looker'

# Helper functions
def get_project_path(project_name):
    if not project_name:
        return None, "project_name is required."
    location = os.path.join(base_path, project_name)
    return location

def get_lookml_hub_path():
    return os.path.join(base_path, lookml_hub)

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
        try:
            parsed = lkml.load(f)
        except SyntaxError as e:
            print(f"Error parsing {file_path}: {e}")
            return []

    view_relations = []
    for view in parsed.get('views', []):
        view_name = view.get('name')
        extends_list = view.get('extends', [])
        
        if 'extends__all' in view:
            for sublist in view['extends__all']:
                extends_list.extend(sublist)
                
        if view_name.startswith('+'):
            extends_list.append(view_name.lstrip('+'))
        
        for ext in extends_list:
            view_relations.append((view_name, ext))
    
    return view_relations

def check_derived_table(file_path):
    with open(file_path, 'r') as file:
        lookml = lkml.load(file)
        for view in lookml.get('views', []):
            if 'derived_table' in view:
                return True
    return False

def test_01(folder_path_1, folder_path_2, subfolder_name):
    view_names_from_path_1 = set()  # Using set for O(1) lookups
    views_in_subfolder = set()      # Set to track views in '01_Extend_&_Refine' subfolder
    results = []
    
    # Process folder_path_1
    for foldername, _, filenames in os.walk(folder_path_1):
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                view_names_from_path_1.update(extract_all_view_names(file_path))
    
    # Process folder_path_2, specifically the target subfolder
    target_folder_2 = os.path.join(folder_path_2, subfolder_name).lower()  # Ensure case-insensitive matching

    for foldername, _, filenames in os.walk(folder_path_2):
        in_target_subfolder = target_folder_2 in foldername.lower()

        # Extract the part of foldername that comes after the base_folder_name
        path_parts = os.path.normpath(foldername).split(os.sep)
        try:
            base_index = path_parts.index(base_folder_name) + 1  # Start after the base_folder_name
        except ValueError:
            # base_folder_name not in path, continue to next iteration
            continue
        relative_folder_path = os.sep.join(path_parts[base_index:])

        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                relations_from_path_2 = extract_relevant_views(file_path)
                is_derived = check_derived_table(file_path)  # Check if this view has a derived table

                # Extract just the view names from the relations for tracking views in the subfolder
                views_from_path_2 = {view for _, view in relations_from_path_2}

                if in_target_subfolder:
                    views_in_subfolder.update(views_from_path_2)
                
                for extending_view, view_name in relations_from_path_2:
                    derived_status = 'Yes' if is_derived else 'No'
                    if ((view_name in views_in_subfolder and view_name not in view_names_from_path_1) or 
                        (view_name in view_names_from_path_1 and view_name not in views_in_subfolder)):
                        results.append((relative_folder_path, filename, extending_view, view_name, derived_status))

    return results

# Functions for Test 2
def extract_views_derived_table(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    view_details = []
    for view in parsed.get('views', []):
        view_name = view['name']
        derived_status = 'Yes' if 'derived_table' in view else 'No'
        extends_from = view.get('extends__all', [])
        if not isinstance(extends_from, list):
            extends_from = [extends_from]

        view_details.append({
            'view_name': view_name,
            'derived_status': derived_status,
            'extends_from': extends_from
        })
    
    return view_details

def test_02(root_folder, base_folder_name):
    results = []
    views_with_derived_global = set()

    # Focus on the desired sub-folder
    target_folder = os.path.join(root_folder, "03_Spoke_Marts", "01_Common_Marts")
    
    base_path_parts = os.path.normpath(target_folder).split(os.sep)
    base_index = base_path_parts.index(base_folder_name) + 1
    
    for foldername, subfolders, filenames in os.walk(target_folder):
        path_parts = os.path.normpath(foldername).split(os.sep)
        relative_path_parts = path_parts[base_index:]
        relative_path = os.sep.join(relative_path_parts)
        
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(relative_path, filename)
                full_path = os.path.join(foldername, filename)
                view_details = extract_views_derived_table(full_path)

                # Update the global set of views with derived tables
                views_with_derived_global.update(view['view_name'] for view in view_details if view['derived_status'] == 'Yes')

                for view in view_details:
                    # Flatten the extends_from list if it contains sublists
                    flattened_extends_from = [item for sublist in view['extends_from'] for item in (sublist if isinstance(sublist, list) else [sublist])]

                    # Check if the view meets the conditions
                    if (view['derived_status'] == 'No' and 
                        (not view['extends_from'] or not any(ext_view in views_with_derived_global for ext_view in flattened_extends_from))):
                        extend_from_str = ', '.join(flattened_extends_from) if flattened_extends_from else 'None'
                        results.append((file_path, filename, view['view_name'], view['derived_status'], extend_from_str))
    return results

# Functions for Test 3
def extract_relevant_views_test03(file_path):
    try:
        with open(file_path, 'r') as file:
            parsed = lkml.load(file)

        relevant_views = []
        primary_keys = {}
        for item in parsed.get('views', []):
            view_name = item.get('name')
            has_primary_key = False

            # Check if any dimension is a primary key
            for dimension in item.get('dimensions', []):
                if dimension.get('primary_key') == 'yes':
                    has_primary_key = True
                    primary_keys[view_name] = dimension.get('name')
                    break  # No need to check other dimensions if primary key found

            # Add the view to relevant_views only if it has a primary key
            if view_name and "+" not in view_name and not item.get('extends__all') and has_primary_key:
                relevant_views.append(view_name)

        return relevant_views, primary_keys

    except SyntaxError as e:
        print(f"SyntaxError in file: {file_path}")
        print(f"Error details: {e}")
        return [], {}

def extract_assert_blocks(lookml_code):
    assert_blocks = re.findall(r'assert:\s+\w+\s*{([^}]+)}', lookml_code, re.DOTALL)
    result = []

    for assert_content in assert_blocks:
        expressions = re.findall(r'expression:\s+\$\{(\w+)\.(\w+)', assert_content, re.DOTALL)
        for expression in expressions:
            value_before_dot = expression[0]
            result.append(value_before_dot)

    return result

def is_view_in_test(view_name, test_names):
    # Check if view name is part of any test name
    for test_name in test_names:
        print(f"Checking view: {view_name}")
        print(f"Checking test: {test_name}")
        if view_name in test_name:
            return True
    return False

def process_folder(root_folder, base_folder_name):
    all_views_with_details = []  # To store view details along with file path and name
    all_tests = []
    all_primary_keys = {} 

    # First pass: Collect all view names along with their file details
    for foldername, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.lkml'):
                file_path = os.path.join(foldername, filename)
                relevant_views, primary_keys = extract_relevant_views_test03(file_path)
                for view in relevant_views:
                    all_views_with_details.append((os.path.relpath(foldername, root_folder), filename, view))
                all_primary_keys.update(primary_keys)

    # Second pass: Collect all test names
    for foldername, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.lkml'):
                file_path = os.path.join(foldername, filename)
                with open(file_path, 'r') as file:
                    content = file.read()
                    test_names = extract_assert_blocks(content)
                    all_tests.extend(test_names)

    return all_views_with_details, all_tests, all_primary_keys

def test_03(all_views_with_details, all_tests, all_primary_keys):
    views_not_in_test = []
    for folder_path, file_name, view in all_views_with_details:
        if not any(view in test for test in all_tests):
            # Add primary key dimension name if available
            primary_key = all_primary_keys.get(view, "N/A")
            views_not_in_test.append((folder_path, file_name, view, primary_key))  # Ensure 4 elements are added
    return views_not_in_test

# Functions for Test 4
def test_04(folder_path_1, folder_path_2):
    # Extract all view names from folder_path_1
    view_names_from_path_1 = set()
    for foldername, _, filenames in os.walk(folder_path_1):
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                view_names_from_path_1.update(extract_all_view_names(file_path))

    # Initialize results list
    results = []

    # Iterate through folder_path_2 to find relevant views
    for foldername, _, filenames in os.walk(folder_path_2):
        
        # Extract the part of foldername that comes after the base_folder_name
        path_parts = os.path.normpath(foldername).split(os.sep)
        try:
            base_index = path_parts.index(base_folder_name) + 1  # Start after the base_folder_name
        except ValueError:
            # base_folder_name not in path, continue to next iteration
            continue
        relative_folder_path = os.sep.join(path_parts[base_index:])

        for filename in filenames:
            if filename.endswith('.view.lkml') and '_r' not in filename:
                file_path = os.path.join(foldername, filename)
                view_relations = extract_relevant_views(file_path)
                for extending_view, extended_view in view_relations:
                    if extended_view in view_names_from_path_1:
                        derived_status = 'Yes' if check_derived_table(file_path) else 'No'
                        results.append((relative_folder_path, filename, extending_view, extended_view, derived_status))
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
    base_index = base_path_parts.index(base_folder_name)+1
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        path_parts = os.path.normpath(foldername).split(os.sep)
        relative_path = os.sep.join(path_parts[base_index:])
        
        # Only consider folders starting with "02_" and ending with "_Marts"
        if path_parts[-1] not in ('01_Common_Marts', '03_Spoke_Marts') and path_parts[-1].endswith('_Marts'):
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
    base_index = base_path_parts.index(base_folder_name)+1
    
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
                        if f"{view_name}" in fields_content:
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
                            for kind in ['dimensions', 'measures', 'dimension_groups']:
                                for item in view.get(kind, []):
                                    parameters = list(item.keys())
                                    expected_order, current_order = check_parameter_order(parameters, parameter_hierarchy)
                                    if expected_order and current_order:
                                        relative_path = os.path.relpath(root, base_path)
                                        results.append((relative_path, file, view_name, item.get('name', ''), matched_explores, kind, expected_order, current_order))
    
    return results

# Functions for Test 11
def extract_includes_with_indentation(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    includes_with_indent = []
    for line in lines:
        if line.startswith((' ', '\t')) and 'include:' in line:
            includes_with_indent.append(line.strip())

    return includes_with_indent

def test_11(root_folder, base_folder_name):
    indented_includes = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                includes = extract_includes_with_indentation(file_path)
                for include_statement in includes:
                    indented_includes.append((relative_path, filename, include_statement))
    
    return indented_includes

# Functions for Test 12
def extract_fields(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    fields = []
    for view in parsed.get('views', []):
        view_name = view['name']
        if view_name.startswith('+') or 'extends__all' in view:  # Only consider views starting with '+', and not containing 'extends'
            for dim in view.get('dimensions', []):
                dim_name = dim['name']
                parameters = list(dim.keys())
                if 'sql' in parameters or 'type' in parameters:
                    fields.append((view_name, "dimension", dim_name))
            
            for measure in view.get('measures', []):
                measure_name = measure['name']
                parameters = list(measure.keys())
                if 'sql' in parameters or 'type' in parameters:
                    fields.append((view_name, "measure", measure_name))
    
    return fields

def test_12(root_folder, base_folder_name, subfolder=""):
    relevant_fields = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    target_folder = os.path.join(root_folder, subfolder) if subfolder else root_folder
    
    for foldername, subfolders, filenames in os.walk(target_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                fields = extract_fields(file_path)
                for view_name, field_type, field_name in fields:
                    relevant_fields.append((relative_path, filename, view_name, field_type, field_name))
    
    return relevant_fields

# Functions for Test 13
def extract_views_with_extends(file_path):
    try:
        with open(file_path, 'r') as file:
            parsed = lkml.load(file)

        views_with_extends = []
        for item in parsed.get('views', []):
            view_name = item.get('name')
            extends = item.get('extends__all')
            if view_name and extends:
                # The structure of extends is a list of lists
                for extend_group in extends:
                    for extend_view in extend_group:
                        views_with_extends.append((view_name, extend_view))
        return views_with_extends

    except SyntaxError as e:
        print(f"SyntaxError in file: {file_path}")
        print(f"Error details: {e}")
        return []

def process_folder_test13(root_folder):
    all_extends = []
    view_to_extends_map = {}  # Map each view to what it extends

    # Extract views and their extends
    for foldername, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.lkml'):
                file_path = os.path.join(foldername, filename)
                views_with_extends = extract_views_with_extends(file_path)
                for view, extend in views_with_extends:
                    view_to_extends_map[view] = extend
                    
                    all_extends.append({
                        "folder_path": os.path.relpath(foldername, root_folder),
                        "file_name": filename,
                        "view_name": view,
                        "extends": extend
                    })

    return all_extends, view_to_extends_map

def find_extension_chains(all_extends, view_to_extends_map):
    extension_chains = []
    for view_detail in all_extends:
        extending_view = view_detail["extends"]
        # Check if this extending view is itself an extending view in the map
        if extending_view in view_to_extends_map:
            extended_by_extending = view_to_extends_map[extending_view]
            view_detail["extends_extends"] = extended_by_extending  # Add second level of extends
            extension_chains.append(view_detail)

    return extension_chains

# Functions for Test 14
def extract_joins(file_path, explore_filename):
    try:
        with open(file_path, 'r') as f:
            parsed = lkml.load(f)
        
        joins_info = []
        for explore in parsed.get('explores', []):
            # Instead of the explore name, we will use the explore_filename parameter
            explore_name = explore_filename
            for join in explore.get('joins', []):
                join_type = join.get('type', '')
                relationship = join.get('relationship', '')
                if join_type != 'left_outer' or relationship != 'many_to_one':
                    # Get join content with indentation as it appears in the LookML file
                    join_content = lkml.dump({'joins': [join]})
                    joins_info.append((explore_name, join_content))
        
        return joins_info
    
    except SyntaxError as e:
        print(f"SyntaxError in file: {file_path}")
        print(f"Error details: {e}")
        return []

def test_14(root_folder, base_folder_name):
    invalid_joins = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        for filename in filenames:
            if filename.endswith('.explore.lkml'):
                file_path = os.path.join(foldername, filename)
                # When calling the extract_joins function, pass the filename as the second argument
                joins = extract_joins(file_path, filename.replace('.explore.lkml', ''))
                for explore_name, join_content in joins:
                    invalid_joins.append((relative_path, explore_name, join_content))
    
    return invalid_joins

# Functions for Test 15
def test_15(file, folder, explore_name, parameters, parameter_hierarchy, results):
    # Check the order
    correct_order = True
    last_index = -1
    filtered_params = [param for param in parameter_hierarchy if param in parameters]

    for param in filtered_params:
        param_index = parameter_hierarchy.index(param)
        if param_index < last_index:
            correct_order = False
            break
        last_index = param_index

    # Check for blank values
    blank_params = [param for param in parameter_hierarchy if param in parameters and parameters[param].strip('"').strip() == ""]

    # Check if all parameters in parameter_hierarchy are present
    missing_params = [param for param in parameter_hierarchy if param not in parameters]

    if not correct_order or missing_params or blank_params:
        parameter_order_str = ', '.join([f"{param}" for param in parameter_hierarchy if param in filtered_params])
        current_order_str = ', '.join(filtered_params)
        missing_params_str = ', '.join(missing_params)
        blank_params_str = ', '.join(blank_params)
        results.append((folder, file, explore_name, parameter_order_str, current_order_str, missing_params_str, blank_params_str))

# Functions for Test 16
def extract_dimensions(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    dimensions = []
    for view in parsed.get('views', []):
        view_name = view['name']
        for dim in view.get('dimensions', []):
            dim_name = dim['name']
            parameters = list(dim.keys())
            dimensions.append((view_name, dim_name, parameters))
    
    return dimensions

def test_16(root_folder, base_folder_name):
    wrong_dimensions = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                dimensions = extract_dimensions(file_path)
                for view_name, dim_name, parameters in dimensions:
                    if 'primary_key' in parameters and "03_Spoke_Marts" not in relative_path:
                        stripped_view_name = view_name.lstrip('+')
                        explores = get_explore_names(root_folder, stripped_view_name)
                        wrong_dimensions.append((relative_path, view_name, dim_name, filename, explores))
    
    return wrong_dimensions

# Functions for Test 17
def check_parameter_order_test17(parameters, parameter_hierarchy, required_values):
    correct_order = True
    last_index = -1
    filtered_params = [param for param in parameters if param in parameter_hierarchy]
    missing_params = set(parameter_hierarchy) - set(filtered_params)
    incorrect_values = {}

    for param in filtered_params:
        param_index = parameter_hierarchy.index(param)
        if param_index < last_index:
            correct_order = False

        if param in required_values and parameters[param] != required_values[param]:
            incorrect_values[param] = parameters[param]

        last_index = param_index

    if correct_order and not incorrect_values and not missing_params:
        return None, None, None, None

    parameter_order_str = ', '.join([param for param in parameter_hierarchy if param in filtered_params])
    current_order_str = ', '.join([f"{param}({parameters.get(param, 'None')})" for param in filtered_params])
    missing_params_str = ', '.join(missing_params)
    incorrect_values_str = ', '.join([f"{k}({v})" for k, v in incorrect_values.items()])
    
    return parameter_order_str, current_order_str, missing_params_str, incorrect_values_str


def extract_dimensions_test17(file_path, parameter_hierarchy):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)

    dimensions = []
    for view in parsed.get('views', []):
        view_name = view['name']
        for dim in view.get('dimensions', []):
            dim_name = dim['name']
            parameters = {k: v for k, v in dim.items() if k in parameter_hierarchy}
            dimensions.append((view_name, dim_name, parameters))

    return dimensions

def test_17(root_folder, base_folder_name):
    wrong_dimensions = []
    parameter_hierarchy = ['primary_key', 'hidden', 'type']
    required_values = {'primary_key': 'yes', 'hidden': 'yes'}
        
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                dimensions = extract_dimensions_test17(file_path, parameter_hierarchy)
                for view_name, dim_name, parameters in dimensions:
                    stripped_view_name = view_name.lstrip('+')
                    matched_explores = get_explore_names(base_path, stripped_view_name)
                    if 'primary_key' in parameters:
                        expected_order, current_order, missing_params, incorrect_values = check_parameter_order_test17(parameters, parameter_hierarchy, required_values)
                        if expected_order or missing_params or incorrect_values:
                            wrong_dimensions.append((relative_path, view_name, dim_name, matched_explores, expected_order, current_order, missing_params, incorrect_values))
    
    return wrong_dimensions

# Functions for Test 18
def extract_dimensions_1(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    dimensions = []
    for view in parsed.get('views', []):
        view_name = view['name']
        for dim in view.get('dimensions', []):
            dim_name = dim['name']
            parameters = dim  # Keep parameters as a dictionary
            dimensions.append((view_name, dim_name, parameters))
    
    return dimensions

def test_18(root_folder, base_folder_name):
    wrong_dimensions = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                dimensions = extract_dimensions_1(file_path)
                for view_name, dim_name, parameters in dimensions:
                    if 'primary_key' in parameters:
                        sql_value = parameters.get('sql', '')
                        stripped_view_name = view_name.lstrip('+')
                        explores = get_explore_names(root_folder, stripped_view_name)
                        if not any(keyword in sql_value for keyword in ["${TABLE}.", "concat", "||", "CONCAT"]):
                            wrong_dimensions.append((relative_path, view_name, dim_name, explores, sql_value))

    return wrong_dimensions

# Functions for Test 19
def test_19(root_folder, base_folder_name):
    wrong_dimensions = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                dimensions = extract_dimensions(file_path)
                for view_name, dim_name, parameters in dimensions:
                    stripped_view_name = view_name.lstrip('+')
                    explores = get_explore_names(root_folder, stripped_view_name)
                    if 'primary_key' in parameters:
                        if ("_pk" not in dim_name and "pk_" not in dim_name and "pri_key" not in dim_name) or "primary_key" in dim_name                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    :
                            wrong_dimensions.append((relative_path, view_name, dim_name, explores))
    
    return wrong_dimensions

# Functions for Test 20
def test_20(directory, root_folder):
    results = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.view.lkml'):
                full_file_path = os.path.join(root, file)
                relative_folder = root.split(root_folder)[-1]
                if relative_folder == '':
                    folder = ''
                else:
                    folder = "/" + relative_folder.lstrip('/').replace('\\', '/') + "/"
                with open(full_file_path, 'r') as f:
                    parsed_content = lkml.load(f)

                for view in parsed_content.get('views', []):
                    view_name = view['name']
                    stripped_view_name = view_name.lstrip('+')
                    for dim_group in view.get('dimension_groups', []):
                        explores = get_explore_names(root_folder, stripped_view_name)
                        dim_group_name = dim_group['name']
                        dim_group_body = dim_group  # Modify this to get specific parts of the body.
                        convert_tz_param = dim_group.get('convert_tz')
                        #print(convert_tz_param)

                        if convert_tz_param != 'no':
                            results.append((folder, file, view_name, dim_group_name, explores))

    return results

# Functions for Test 21
def test_21(directory, root_folder):
    results = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.view.lkml'):
                full_file_path = os.path.join(root, file)
                relative_folder = root.split(root_folder)[-1]
                if relative_folder == '':
                    folder = ''
                else:
                    folder = "/" + relative_folder.lstrip('/').replace('\\', '/') + "/"
                with open(full_file_path, 'r') as f:
                    content = f.read()

                view_blocks = re.split(r'(?=view:\s*[\w+]+\s*{)', content)
                for view_block in view_blocks:
                    if "view:" in view_block:
                        view_name = re.search(r'view:\s*([\w+]+)', view_block)
                        if view_name:
                            view_name = view_name.group(1)
                            sql_table_name = re.search(r'sql_table_name:\s*`([^`]+)`', view_block)
                            derived_table = re.search(r'derived_table\s*:\s*{(.+?)}', view_block, re.DOTALL)
                            if sql_table_name:
                                sql_table_name = sql_table_name.group(1)
                                if "@" not in sql_table_name or 'one-global-dde' in sql_table_name or 'DWH' in sql_table_name or 'DM_VIEWS' in sql_table_name:
                                    results.append((folder, file, view_name, sql_table_name))
                            if derived_table:
                                derived_table = derived_table.group(1).strip()
                                if 'one-global-dde' in derived_table or 'DWH' in derived_table or 'DM_VIEWS' in derived_table:
                                    results.append((folder, file, view_name, derived_table))


    return results

# Functions for Test 22
def test_22(folder_path):
    constants_info = []

    for subdir, _, files in os.walk(folder_path):
        for file in files:
            if file == 'manifest.lkml':
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    constant_blocks = content.split("constant:")[1:]

                    for block in constant_blocks:
                        constant_content = "constant:" + block
                        try:
                            parsed_constant = lkml.load(constant_content)
                            constant = parsed_constant.get('constant')
                            if isinstance(constant, dict):
                                keys = list(constant.keys())
                                extra_keys = [k for k in keys if k not in ['value', 'name']]
                                if extra_keys:
                                    constants_info.append({
                                        'constant_name': constant.get('name', 'Unknown'),
                                        'parameters': ", ".join(extra_keys)
                                    })
                        except Exception as e:
                            print(f"Error parsing constant in {file_path}: {e}")

    return constants_info

# Functions for Test 23
def test_23(base_path):
    base_path_parts = os.path.normpath(base_path).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])

    # Define prefixes to be excluded
    prefixes = ['count_of_', 'sum_of_', 'min_of_', 'max_of_', 'average_of_', 'median_of_']
    
    # Helper function to check if the field name starts with any of the specified prefixes
    def has_invalid_prefix(field_name, sql):
        for prefix in prefixes:
            if field_name.startswith(prefix):
                suffix = field_name[len(prefix):]
                if "${TABLE}" in sql or suffix not in sql:
                    return False
                return True
        return False
    
    measures_info = []
    
    for foldername, subfolders, filenames in os.walk(base_path):
        relative_path = os.path.relpath(foldername, base_path)
        for filename in filenames:
            if filename.endswith('.lkml'):
                file_path = os.path.join(foldername, filename)
                
                with open(file_path, 'r') as file:
                    lkml_content = file.read()
                    parsed_lookml = lkml.load(lkml_content)
                    
                    for view in parsed_lookml.get('views', []):
                        view_name = view.get('name')
                        extends_view_names = []
                        
                        extends = view.get('extends__all')
                        if extends:
                            # Handle nested structure of 'extends__all'
                            for extend_group in extends:
                                for extend_view in extend_group:
                                    extends_view_names.append(extend_view)
                        
                        extends_view_name = ', '.join(extends_view_names)
                        
                        for measure in view.get('measures', []):
                            measure_name = measure.get('name')
                            measure_type = measure.get('type')
                            measure_sql = measure.get('sql')
                            if measure_name and not has_invalid_prefix(measure_name, measure_sql):
                                explore_names = get_explore_names(base_path, view_name)
                                measures_info.append({
                                    'folder_path': relative_path,
                                    'view_file_name': filename,
                                    'view_name': view_name,
                                    'extends_view_name': extends_view_name,
                                    'measure_name': measure_name,
                                    'measure_type': measure_type,
                                    'sql': measure_sql,
                                    'explore_names': explore_names
                                })
    
    return measures_info