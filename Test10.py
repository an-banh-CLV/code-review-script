import lkml
import os
import csv
import re


base_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_pricing_spoke/'
parameter_hierarchy = ['hidden', 'view_label', 'group_label', 'group_item_label', 'label', 'type','description','sql_distinct_key','sql']
results = []


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


# Processing
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
                                if expected_order and current_order: # only add to results if there's a mismatch
                                    relative_path = os.path.relpath(root, base_path)  # Get the relative path
                                    results.append((relative_path, file, view_name, item.get('name', ''), matched_explores, kind, expected_order, current_order))

# Writing to CSV
script_dir = os.path.dirname(os.path.realpath(__file__))
csv_file_path = os.path.join(script_dir, 'Test10.csv')


with open(csv_file_path, 'w', newline='') as csvFile:
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(['folder', 'file_name', 'view_name', 'dimension_name', 'explore_name', 'field_type', 'expected_order', 'current_order'])
    csvWriter.writerows(results)
