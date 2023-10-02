import os
import lkml
import pandas as pd

# Assuming extract_dimensions and check_parameter_order are defined elsewhere in your code
folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_oneforce_spoke/'
base_folder_name = 'ONELooker'

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

def process_folder(root_folder, base_folder_name):
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
                    if 'primary_key' in parameters and 'primary_key' in dim_name:
                        wrong_dimensions.append((relative_path, view_name, dim_name))
    
    return wrong_dimensions

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["File Path", "View Name", "Dimension Name"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    # Sample execution
    results = process_folder(folder_path, base_folder_name)
    write_to_excel(results, "Test19.xlsx")
