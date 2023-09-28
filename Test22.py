import os
import re  
import lkml
import pandas as pd

directory_to_search = 'C:/Users/NC/Documents/ONELooker/LOOKML_one_bkg_doc_spoke/'

def parse_lkml_files(folder_path):
    constants_info = []

    for subdir, _, files in os.walk(folder_path):
        for file in files:
            if file == 'manifest.lkml':
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Split by top-level "constant" key
                    constant_blocks = content.split("constant:")[1:]

                    for block in constant_blocks:
                        constant_content = "constant:" + block
                        print(f"Parsing block: {constant_content[:100]}...")  # Printing the beginning of the block for visibility
                        try:
                            # Parse each individual constant block
                            parsed_constant = lkml.load(constant_content)
                            constant = parsed_constant.get('constant')
                            
                            print(f"Found constant: {constant}")

                            # Check the internal parameters of the constant
                            if isinstance(constant, dict):
                                # Extract the top-level keys
                                keys = list(constant.keys())
                                print(f"keys: {keys}")


                                # Check for any keys other than 'value' and 'name'
                                extra_keys = [k for k in keys if k not in ['value', 'name']]
                                if extra_keys:
                                    constants_info.append({
                                        'constant_name': constant.get('name', 'Unknown'),
                                        'parameters': ", ".join(extra_keys)
                                    })
                        except Exception as e:
                            print(f"Error parsing constant in {file_path}: {e}")

    if constants_info:
        try:
            output_excel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Test22.xlsx')
            df = pd.DataFrame(constants_info)

            writer = pd.ExcelWriter(output_excel_file, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            worksheet = writer.sheets['Sheet1']
            for idx, col in enumerate(df):
                series = df[col]
                max_len = max(series.astype(str).apply(len).max(),  # max length in column
                              len(str(series.name)))  # length of column name/header
                worksheet.set_column(idx, idx, max_len)  # set column width
            writer.close()
            print(f"Saved results to {output_excel_file}")
        except Exception as e:
            print(f"Error writing to Excel: {e}")
    else:
        print("No constants found with extra parameters.")

parse_lkml_files(directory_to_search)
