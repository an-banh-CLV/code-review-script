import os
import lkml
import pandas as pd

folder_path_1 = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_hub/'
folder_path_2 = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_oneforce_spoke/'
subfolder_name = '01_Extend_&_Refine'

def extract_all_view_names(file_path):
    view_names = set()
    
    with open(file_path, 'r') as fileObj:
        try:
            lookml = lkml.load(fileObj)
        except SyntaxError as e:
            print(f"Error parsing {file_path}: {e}")
            return view_names

        if 'views' in lookml:
            for view in lookml['views']:
                if 'name' in view:
                    view_names.add(view['name'])

    return view_names

def extract_relevant_views(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    views_to_check = []
    for view in parsed.get('views', []):
        if 'extends' in view:
            views_to_check.extend(view['extends'])
        if view['name'].startswith('+'):
            views_to_check.append(view['name'].lstrip('+'))
    
    return views_to_check

def process_folders(folder_path_1, folder_path_2, subfolder_name):
    view_names_from_path_1 = set()  # Using set for O(1) lookups
    for foldername, _, filenames in os.walk(folder_path_1):
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                view_names_from_path_1.update(extract_all_view_names(file_path))
    
    # # Printing all view names from folder_path_1
    # print("View Names from folder_path_1:")
    # print(view_names_from_path_1)

    results = []
    target_folder_2 = os.path.join(folder_path_2, subfolder_name)
    views_from_path_2_to_check = set()  # Use a set to store views from path_2 to avoid duplicates
    for foldername, _, filenames in os.walk(target_folder_2):
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                views_from_path_2 = extract_relevant_views(file_path)
                views_from_path_2_to_check.update(views_from_path_2)
                for view_name in views_from_path_2:
                    if view_name not in view_names_from_path_1:
                        results.append((foldername, filename, view_name))

    # Printing the relevant view names from folder_path_2
    # print("Relevant View Names from folder_path_2:")
    # print(views_from_path_2_to_check)
    return results


def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["Folder Path", "File Name", "View Name"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    results = process_folders(folder_path_1, folder_path_2, subfolder_name)
    write_to_excel(results, "Test01.xlsx")
