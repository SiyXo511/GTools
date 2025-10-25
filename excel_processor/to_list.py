import pandas as pd
import os
from .utils import read_file_to_dataframe
import io

def get_column_data(file_or_df, column_name, nan_handling='remove'):
    """
    Extracts a column from a file path or a DataFrame.
    Handles NaN values by either removing them or keeping them (for later conversion to null).
    """
    try:
        if isinstance(file_or_df, str):
            df = read_file_to_dataframe(file_or_df)
        else:
            df = file_or_df

        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the file.")
        
        column_data = df[[column_name]]

        if nan_handling == 'remove':
            # Drop rows where the specific column is NaN
            column_data = column_data.dropna(subset=[column_name])
        
        # Return the series/column data
        return column_data[column_name].tolist()

    except Exception as e:
        print(f"Error in get_column_data: {e}")
        raise

def convert_column_to_list(file_path, column_name, output_folder, nan_handling='remove'):
    """Converts a specific column from an Excel or CSV file to a text file, with each item on a new line."""
    try:
        column_data = get_column_data(file_path, column_name, nan_handling)
        
        # Generate output filename
        base_filename = os.path.basename(file_path)
        name, _ = os.path.splitext(base_filename)
        output_filename = f"{name}_{column_name}_list.txt"
        output_path = os.path.join(output_folder, output_filename)
        
        # Write the list to a text file in comma-separated format [item1,item2,item3]
        with open(output_path, 'w', encoding='utf-8') as f:
            # Convert all items to strings and handle None/NaN values
            data_list = [str(item) if item is not None and not pd.isna(item) else '' for item in column_data]
            # Write as comma-separated list format
            f.write('[' + ', '.join(data_list) + ']')
        
        return output_path
    except Exception as e:
        print(f"Error in convert_column_to_list: {e}")
        raise
