import os
import lkml
import pandas as pd

folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_bkg_doc_spoke/'
base_folder_name = 'ONELooker'

def extract_joins(file_path, explore_filename):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    joins_info = []
    for explore in parsed.get('explores', []):
        # Instead of the explore name, we will use the explore_filename parameter
        explore_name = explore_filename
        for join in explore.get('joins', []):
            join_type = join.get('type', '')
            relationship = join.get('relationship', '')
            if join_type != 'left_outer' or relationship != 'many_to_one':
                # Get join content with indentation as it appears in the LookML file
                join_content = lkml.dump({'joins': [join]})
                joins_info.append((explore_name, join_content))
    
    return joins_info

def process_folder(root_folder, base_folder_name):
    invalid_joins = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        
        for filename in filenames:
            if filename.endswith('.explore.lkml'):
                file_path = os.path.join(foldername, filename)
                # When calling the extract_joins function, pass the filename as the second argument
                joins = extract_joins(file_path, filename.replace('.explore.lkml', ''))
                for explore_name, join_content in joins:
                    invalid_joins.append((relative_path, explore_name, join_content))
    
    return invalid_joins

def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["File Path", "Explore Name", "Join Content"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    results = process_folder(folder_path, base_folder_name)
    write_to_excel(results, "Test14.xlsx")
