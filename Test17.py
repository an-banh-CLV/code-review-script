import os
import lkml
import openpyxl

parameter_hierarchy = ['primary_key', 'hidden', 'type']
folder_path = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_oneforce_spoke/'
base_folder_name = 'ONELooker'

def check_parameter_order(parameters, parameter_hierarchy):
    """Checks the order of parameters against the hierarchy and returns the order as a string."""
    correct_order = True
    last_index = -1
    filtered_params = [param for param in parameters if param in parameter_hierarchy]
    
    for param in filtered_params:
        param_index = parameter_hierarchy.index(param)
        if param_index < last_index:
            correct_order = False
            break
        last_index = param_index

    if correct_order:
        return None, None

    parameter_order_str = ', '.join([param for param in parameter_hierarchy if param in filtered_params])
    current_order_str = ', '.join([param for param in filtered_params])
    return parameter_order_str, current_order_str

def extract_dimensions(file_path):
    with open(file_path, 'r') as f:
        parsed = lkml.load(f)
    
    dimensions = []
    for view in parsed.get('views', []):
        view_name = view['name']
        for dim in view.get('dimensions', []):
            dim_name = dim['name']
            parameters = list(dim.keys())
            dimensions.append((view_name, dim_name, parameters))
    
    return dimensions

def process_folder(root_folder, base_folder_name):
    wrong_dimensions = []
    
    base_path_parts = os.path.normpath(root_folder).split(os.sep)
    base_path = os.sep.join(base_path_parts[:base_path_parts.index(base_folder_name) + 1])
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        relative_path = os.path.relpath(foldername, base_path)
        for filename in filenames:
            if filename.endswith('.view.lkml'):
                file_path = os.path.join(foldername, filename)
                dimensions = extract_dimensions(file_path)
                for view_name, dim_name, parameters in dimensions:
                    if 'primary_key' in parameters:
                        expected_order, current_order = check_parameter_order(parameters, parameter_hierarchy)
                        if expected_order and current_order:
                            wrong_dimensions.append((relative_path, view_name, dim_name, expected_order, current_order))

    
    return wrong_dimensions

def export_to_excel(data, filepath):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Results"

    headers = ['Folder', 'View Name', 'Dimension Name', 'Expected Order', 'Current Order']
    ws.append(headers)

    for row in data:
        ws.append(row)

    for column in ws.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column[0].column_letter].width = adjusted_width

    wb.save(filepath)

if __name__ == "__main__":
    wrong_dimensions = process_folder(folder_path, base_folder_name)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_to_excel(wrong_dimensions, os.path.join(script_dir, "Test17.xlsx"))
    print("Results exported to Test17.xlsx in the script's directory.")
