import pandas as pd
import os
import json
from .utils import read_file_to_dataframe

def convert_json_to_table(json_file_path, output_format, output_folder):
    """
    Reads a JSON file and converts it to CSV or Excel format.
    Expects JSON file to contain a list of objects (records).
    """
    try:
        # Read JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Validate that it's a list of objects
        if not isinstance(json_data, list):
            raise ValueError("JSON file must contain a list of objects")
        
        if len(json_data) == 0:
            raise ValueError("JSON file is empty")
        
        # Convert to DataFrame
        df = pd.DataFrame(json_data)
        
        # Generate output filename
        base_filename = os.path.basename(json_file_path)
        name, _ = os.path.splitext(base_filename)
        
        if output_format == 'csv':
            output_filename = f"{name}_converted.csv"
            output_path = os.path.join(output_folder, output_filename)
            df.to_csv(output_path, index=False, encoding='utf-8')
        elif output_format == 'xlsx':
            output_filename = f"{name}_converted.xlsx"
            output_path = os.path.join(output_folder, output_filename)
            df.to_excel(output_path, index=False)
        elif output_format == 'xls':
            output_filename = f"{name}_converted.xls"
            output_path = os.path.join(output_folder, output_filename)
            df.to_excel(output_path, index=False)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        return output_path
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error converting JSON to table: {str(e)}")

def get_json_preview(json_file_path, max_rows=5):
    """
    Reads a JSON file and returns a preview of the data structure.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        if not isinstance(json_data, list):
            return {"error": "JSON file must contain a list of objects"}
        
        if len(json_data) == 0:
            return {"error": "JSON file is empty"}
        
        # Get preview data
        preview_data = json_data[:max_rows]
        
        # Get column names from first object
        if preview_data:
            columns = list(preview_data[0].keys())
        else:
            columns = []
        
        return {
            "preview": preview_data,
            "columns": columns,
            "total_rows": len(json_data)
        }
        
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON format: {str(e)}"}
    except Exception as e:
        return {"error": f"Error reading JSON file: {str(e)}"}