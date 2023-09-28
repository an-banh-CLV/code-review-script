import os
import lkml
import pandas as pd

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_bkg_doc_spoke/'
base_folder_name = 'ONELooker'

def extract_views_without_derived_table(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    views_without_derived_table = []
    for view in parsed.get('views', []):
        if 'derived_table' not in view:
            views_without_derived_table.append(view['name'])
    
    return views_without_derived_table

def process_folder(root_folder, base_folder_name):
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

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["File Path", "File Name", "View Name"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    results = process_folder(folder_path, base_folder_name)
    write_to_excel(results, "Test02.xlsx")
