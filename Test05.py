import os
import lkml
import pandas as pd

# check if any explore.lkml file is not under sub-folder 02_Models

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_bkg_doc_spoke/'
base_folder_name = 'ONELooker'

def check_explore_outside_models(root_folder, base_folder_name):
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

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["Folder Path", "File Name"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    results = check_explore_outside_models(folder_path, base_folder_name)
    write_to_excel(results, "Test05.xlsx")
