import os
import lkml
import pandas as pd

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_oneforce_spoke/'
base_folder_name = 'ONELooker'

def extract_view_names(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    return [view['name'] for view in parsed.get('views', [])]

def process_folder(root_folder, base_folder_name):
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

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["File Path", "File Name", "View Name"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    results = process_folder(folder_path, base_folder_name)
    write_to_excel(results, "Test09.xlsx")
