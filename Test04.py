import os
import pandas as pd

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_bkg_doc_spoke'
base_folder_name = 'ONELooker'
target_subfolder = "01_Extend_&_Refine"

def process_folder(root_folder, base_folder_name, target_subfolder):
    results = []
    
    # Add the target subfolder to the root folder path
    full_folder_path = os.path.join(root_folder, target_subfolder)
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_index = base_path_parts.index(base_folder_name)
    
    for foldername, subfolders, filenames in os.walk(full_folder_path):
        path_parts = os.path.normpath(foldername).split(os.sep)
        relative_path = os.sep.join(path_parts[base_index:])
        
        for filename in filenames:
            if filename.endswith('.view.lkml') and not filename.endswith('_r.view.lkml'):
                file_path = os.path.join(relative_path, filename)
                results.append((file_path, filename))
    
    return results

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["File Path", "File Name"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    results = process_folder(folder_path, base_folder_name, target_subfolder)
    write_to_excel(results, "Test04.xlsx")
