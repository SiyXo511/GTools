import pandas as pd
import os

def read_file_to_dataframe(file_path):
    """
    Reads a file into a pandas DataFrame, supporting both Excel and CSV.
    
    :param file_path: Path to the input Excel or CSV file.
    :return: A pandas DataFrame.
    """
    _, extension = os.path.splitext(file_path)
    if extension.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    elif extension.lower() == '.csv':
        return pd.read_csv(file_path, encoding='utf-8')
    else:
        raise ValueError(f"Unsupported file type: {extension}")
