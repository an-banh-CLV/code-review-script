import os
import lkml
import pandas as pd

# Compare number of explore.lkml files and lkml files containing test parameter

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_bkg_doc_spoke/'
base_folder_name = 'ONELooker'

def extract_test_param_files(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    if "test:" in content:
        return True
    return False

def process_folder(root_folder, base_folder_name):
    relevant_fields = []
    explore_files = []
    test_param_files = []

    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, _, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        for filename in filenames:
            if filename.endswith('.explore.lkml'):
                explore_files.append((relative_path, filename))
            
            if filename.endswith('.lkml') and extract_test_param_files(os.path.join(foldername, filename)):
                test_param_files.append((relative_path, filename))
    
    return explore_files, test_param_files

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["Folder Path", "File Name"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    explore_results, test_param_results = process_folder(folder_path, base_folder_name)
    
    if len(explore_results) != len(test_param_results):
        results = explore_results + test_param_results
        write_to_excel(results, "Test03.xlsx")
