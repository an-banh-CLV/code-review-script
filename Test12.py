import os
import lkml
import pandas as pd

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_pricing_spoke/'
base_folder_name = 'ONELooker'
subfolder_name = '01_Extend_&_Refine'

def extract_fields(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    fields = []
    for view in parsed.get('views', []):
        view_name = view['name']
        print(view_name)
        if view_name.startswith('+') and 'extends' not in view:  # Only consider views starting with '+', and not containing 'extends'
            for dim in view.get('dimensions', []):
                dim_name = dim['name']
                print(dim_name)

                parameters = list(dim.keys())
                if 'sql' in parameters or 'type' in parameters:
                    fields.append((view_name, "dimension", dim_name))
            
            for measure in view.get('measures', []):
                measure_name = measure['name']
                parameters = list(measure.keys())
                if 'sql' in parameters or 'type' in parameters:
                    fields.append((view_name, "measure", measure_name))
    
    return fields

def process_folder(root_folder, base_folder_name, subfolder=""):
    relevant_fields = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    target_folder = os.path.join(root_folder, subfolder) if subfolder else root_folder
    
    
    for foldername, subfolders, filenames in os.walk(target_folder):
        relative_path = os.path.relpath(foldername, base_path)
        # print(f"Target folder: {relative_path}")
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                # print(f"Checking file: {filename}")
                file_path = os.path.join(foldername, filename)
                fields = extract_fields(file_path)
                for view_name, field_type, field_name in fields:
                    relevant_fields.append((relative_path, filename, view_name, field_type, field_name))
    
    return relevant_fields

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["File Path", "File Name", "View Name", "Field Type", "Field Name"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    results = process_folder(folder_path, base_folder_name, subfolder_name)
    write_to_excel(results, "Test12.xlsx")