import os
import re
import pandas as pd
import lkml

base_path = 'C:/Users/minha/OneDrive/Documents/LOOKML_one_space_yield_spoke'
base_folder_name = 'Documents'

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

def get_non_prefixed_measures(base_path):
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

# Example usage
# Convert the results to a pandas DataFrame
measures_info = get_non_prefixed_measures(base_path)
df = pd.DataFrame(measures_info)

# Save the DataFrame to an Excel file
output_file = 'measures_info.xlsx'
df.to_excel(output_file, index=False)

print(f"Results have been written to {output_file}")
