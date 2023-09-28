import os
import lkml
import pandas as pd

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_bkg_doc_spoke/'
base_folder_name = 'ONELooker'

def extract_dimensions(file_path):
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
                    if 'primary_key' in parameters:
                        sql_value = parameters.get('sql', '')
                        if not any(keyword in sql_value for keyword in ["${TABLE}.", "concat", "||", "CONCAT"]):
                            wrong_dimensions.append((relative_path, view_name, dim_name, sql_value))

    return wrong_dimensions



def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["File Path", "View Name", "Dimension Name", "SQL Value"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    # Sample execution
    results = process_folder(folder_path, base_folder_name)
    write_to_excel(results, "Test18.xlsx")

