import os
import lkml
import pandas as pd
import re

folder_path = 'C:/Users/Rever/Documents/ONELooker/LOOKML_one_oneforce_spoke/'
base_folder_name = 'ONELooker'

def extract_relevant_views(file_path):
    with open(file_path, 'r') as file:
        parsed = lkml.load(file)

    relevant_views = []
    primary_keys = {}
    for item in parsed.get('views', []):
        view_name = item.get('name')
        if view_name and "+" not in view_name and not item.get('extends__all'):
            relevant_views.append(view_name)

            # Checking for primary key dimensions
            for dimension in item.get('dimensions', []):
                if dimension.get('primary_key') == 'yes':
                    primary_keys[view_name] = dimension.get('name')
    return relevant_views, primary_keys


def extract_test_names(file_content):
    # Regular expression to extract test names
    # Adjust this regex based on your file structure and test naming conventions
    test_names = re.findall(r'test:\s*([\w_]+)\s*\{', file_content)
    return test_names

def is_view_in_test(view_name, test_names):
    # Check if view name is part of any test name
    for test_name in test_names:
        print(f"Checking view: {view_name}")
        print(f"Checking test: {test_name}")
        if view_name in test_name:
            return True
    return False

def process_folder(root_folder, base_folder_name):
    all_views_with_details = []  # To store view details along with file path and name
    all_tests = []
    all_primary_keys = {} 

    # First pass: Collect all view names along with their file details
    for foldername, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.lkml'):
                file_path = os.path.join(foldername, filename)
                relevant_views, primary_keys = extract_relevant_views(file_path)
                for view in relevant_views:
                    all_views_with_details.append((os.path.relpath(foldername, root_folder), filename, view))
                all_primary_keys.update(primary_keys)

    # Second pass: Collect all test names
    for foldername, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.lkml'):
                file_path = os.path.join(foldername, filename)
                with open(file_path, 'r') as file:
                    content = file.read()
                    test_names = extract_test_names(content)
                    all_tests.extend(test_names)

    return all_views_with_details, all_tests, all_primary_keys

def find_views_not_in_tests(all_views_with_details, all_tests, all_primary_keys):
    views_not_in_test = []
    for folder_path, file_name, view in all_views_with_details:
        if not any(view in test for test in all_tests):
            # Add primary key dimension name if available
            primary_key = all_primary_keys.get(view, "N/A")
            views_not_in_test.append((folder_path, file_name, view, primary_key))  # Ensure 4 elements are added
    return views_not_in_test


def write_to_excel(data, output_file):
    df = pd.DataFrame(data, columns=["Folder Path", "File Name", "View Name", "Primary Key Dimension"])
    df.to_excel(output_file, index=False)

if __name__ == '__main__':
    all_views_with_details, all_tests, all_primary_keys = process_folder(folder_path, base_folder_name)
    views_not_in_tests = find_views_not_in_tests(all_views_with_details, all_tests, all_primary_keys)
    write_to_excel(views_not_in_tests, "Test03.xlsx")
