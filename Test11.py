import os
import lkml
import pandas as pd

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_oneforce_spoke/'
base_folder_name = 'ONELooker'

def extract_includes_with_indentation(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    includes_with_indent = []
    for line in lines:
        if line.startswith((' ', '\t')) and 'include:' in line:
            includes_with_indent.append(line.strip())

    return includes_with_indent

def process_folder(root_folder, base_folder_name):
    indented_includes = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                includes = extract_includes_with_indentation(file_path)
                for include_statement in includes:
                    indented_includes.append((relative_path, filename, include_statement))
    
    return indented_includes

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["File Path", "File Name", "Include Statement"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    results = process_folder(folder_path, base_folder_name)
    write_to_excel(results, "Test11.xlsx")
