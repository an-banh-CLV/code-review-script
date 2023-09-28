import os
import pandas as pd

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_bkg_doc_spoke/'
base_folder_name = 'ONELooker'

def extract_includes(file_path):
    with open(file_path, 'r') as f:
        content = f.readlines()

    include_statements = [line.strip() for line in content if line.startswith('include:') and '/explore.lkml' in line]
    
    return include_statements

def process_folder(root_folder, base_folder_name):
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

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["File Path", "File Name", "Include Statement"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    results = process_folder(folder_path, base_folder_name)
    write_to_excel(results, "Test07.xlsx")
