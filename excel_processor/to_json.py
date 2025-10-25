import pandas as pd
import os
import json
from .utils import read_file_to_dataframe

def _dataframe_to_records_with_nested_json(df):
    """
    Converts a DataFrame to a list of dictionaries, attempting to parse
    string values as nested JSON and handling NaNs.
    """
    list_of_records = []
    for _, row in df.iterrows():
        record = {}
        for col_name, value in row.items():
            # Convert NaN values to None for JSON compatibility
            if pd.isna(value):
                record[col_name] = None
            elif isinstance(value, str):
                try:
                    record[col_name] = json.loads(value)
                except json.JSONDecodeError:
                    record[col_name] = value # Not a JSON string, keep as is
            else:
                record[col_name] = value
        list_of_records.append(record)
        
    return list_of_records

def get_columns_as_json_records(file_path, column_names):
    """
    Reads a file and returns the data from specific columns as a list of dictionaries.
    Handles NaN values and nested JSON strings.
    """
    df = read_file_to_dataframe(file_path)
    # Check if all requested columns exist
    for col in column_names:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in the file.")
    
    selected_df = df[column_names]
    return _dataframe_to_records_with_nested_json(selected_df)

def convert_columns_to_json(file_path, column_names, output_folder):
    """
    Reads an Excel or CSV file, extracts specific columns, and saves them as a JSON file.
    """
    try:
        json_records = get_columns_as_json_records(file_path, column_names)
        
        base_filename = os.path.basename(file_path)
        name, _ = os.path.splitext(base_filename)
        output_filename = f"{name}_selected_columns.json"
        output_path = os.path.join(output_folder, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_records, f, indent=4, ensure_ascii=False)
            
        return output_path
    except Exception as e:
        print(f"An error occurred in convert_columns_to_json: {e}")
        return None

def add_json_column_to_file(file_path, column_names, output_folder):
    """
    Adds a new column to the original file, where each cell contains a JSON object
    of the selected columns for that row.
    """
    try:
        df = read_file_to_dataframe(file_path)
        # Check if all requested columns exist
        for col in column_names:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in the file.")

        # Get records with properly parsed nested JSON
        json_records = _dataframe_to_records_with_nested_json(df[column_names])
        
        # Convert each record back to a clean JSON string for the new column
        df['Generated_JSON'] = [json.dumps(record, ensure_ascii=False) for record in json_records]

        base_filename = os.path.basename(file_path)
        name, ext = os.path.splitext(base_filename)
        output_filename = f"{name}_with_json_col{ext}"
        output_path = os.path.join(output_folder, output_filename)
        
        # Save the modified dataframe back to a new file in its original format
        if ext.lower() in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
        elif ext.lower() == '.csv':
            df.to_csv(output_path, index=False)
        else:
            raise ValueError(f"Unsupported output file format: {ext}")

        return output_path
    except Exception as e:
        print(f"An error occurred in add_json_column_to_file: {e}")
        return None
