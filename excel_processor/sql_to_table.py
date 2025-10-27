import pandas as pd
import re
import os
from io import StringIO


def parse_sql_insert(sql_text):
    """
    Parse SQL INSERT statements and extract data into a list of dictionaries.
    Supports single and multiple INSERT statements.
    
    Args:
        sql_text: SQL INSERT statement(s) as string
        
    Returns:
        List of dictionaries (records) extracted from SQL
    """
    # Remove comments
    sql_text = re.sub(r'--.*?$', '', sql_text, flags=re.MULTILINE)
    sql_text = re.sub(r'/\*.*?\*/', '', sql_text, flags=re.DOTALL)
    
    all_records = []
    
    # Find all INSERT INTO statements - use a simple approach
    insert_positions = []
    i = 0
    while i < len(sql_text):
        match = re.search(r'INSERT\s+INTO\s+', sql_text[i:], re.IGNORECASE)
        if not match:
            break
        insert_positions.append(i + match.start())
        i += match.end()
    
    for insert_pos in insert_positions:
        # Find the opening parenthesis after table name
        i = insert_pos
        while i < len(sql_text) and sql_text[i] != '(':
            i += 1
        
        if i >= len(sql_text):
            continue
        
        # Extract column names (content between first ( and ))
        depth = 1
        start_idx = i + 1
        i += 1
        
        while i < len(sql_text) and depth > 0:
            if sql_text[i] == '(':
                depth += 1
            elif sql_text[i] == ')':
                depth -= 1
            i += 1
        
        if depth != 0:
            continue
        
        columns_str = sql_text[start_idx:i-1]
        
        # Find VALUES keyword
        remaining_text = sql_text[i:]
        values_match = re.search(r'VALUES\s*', remaining_text, re.IGNORECASE)
        if not values_match:
            continue
        
        values_start = i + values_match.end()
        
        # Find the end of this INSERT statement
        next_insert_match = re.search(r'INSERT\s+INTO\s+', sql_text[values_start:], re.IGNORECASE)
        if next_insert_match:
            values_str = sql_text[values_start:values_start + next_insert_match.start()]
        else:
            values_str = sql_text[values_start:]
        
        # Parse column names
        columns = []
        for col in columns_str.split(','):
            col = col.strip()
            # Remove backticks if present
            if col.startswith('`') and col.endswith('`'):
                col = col[1:-1]
            columns.append(col)
        
        # Parse value rows - extract content between parentheses
        value_groups = []
        depth = 0
        start_idx = -1
        
        for j, char in enumerate(values_str):
            if char == '(' and depth == 0:
                start_idx = j + 1
                depth = 1
            elif char == '(':
                depth += 1
            elif char == ')' and depth == 1:
                value_groups.append(values_str[start_idx:j])
                depth = 0
            elif char == ')':
                depth -= 1
        
        # Parse each value group
        for value_group in value_groups:
            values = parse_values(value_group)
            
            # Handle mismatch between column count and value count
            if len(values) != len(columns):
                # If fewer values than columns, pad with None
                if len(values) < len(columns):
                    values.extend([None] * (len(columns) - len(values)))
                # If more values than columns, truncate to match
                else:
                    values = values[:len(columns)]
            
            # Create dictionary record
            record = {}
            for col, val in zip(columns, values):
                record[col] = val
            
            all_records.append(record)
    
    return all_records


def parse_values(value_string):
    """Parse a comma-separated list of values, respecting quoted strings."""
    values = []
    current_value = ''
    in_quotes = False
    quote_char = None
    i = 0
    
    while i < len(value_string):
        char = value_string[i]
        
        if char in ["'", '"'] and not in_quotes:
            in_quotes = True
            quote_char = char
            current_value += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current_value += char
        elif char == ',' and not in_quotes:
            values.append(clean_value(current_value.strip()))
            current_value = ''
        else:
            current_value += char
        
        i += 1
    
    # Add the last value
    if current_value:
        values.append(clean_value(current_value.strip()))
    
    return values


def clean_value(val):
    """Clean and convert a value string to appropriate Python type."""
    if not val:
        return None
    
    # Handle NULL
    if val.upper() == 'NULL':
        return None
    
    # Handle quoted strings
    if val.startswith("'") and val.endswith("'"):
        result = val[1:-1].replace("''", "'")
    elif val.startswith('"') and val.endswith('"'):
        result = val[1:-1].replace('""', '"')
    else:
        # Try to parse as number
        try:
            if '.' in val:
                return float(val)
            else:
                return int(val)
        except ValueError:
            result = val
    
    # Clean invisible/special characters from strings
    if isinstance(result, str):
        # Remove zero-width characters and control characters
        import unicodedata
        # Replace invisible/control characters with space
        result = ''.join(char for char in result if unicodedata.category(char)[0] != 'C' or char in '\n\r\t')
        # Remove zero-width characters
        result = result.translate(str.maketrans('', '', '\u200b\u200c\u200d\ufeff'))
    
    # Ensure result is safe for Excel export (convert dicts and lists to strings)
    if isinstance(result, (dict, list)):
        import json
        return json.dumps(result, ensure_ascii=False)
    
    # Convert to string if it's not a basic type
    if not isinstance(result, (str, int, float, type(None))):
        result = str(result)
    
    return result


def sql_to_dataframe(sql_text):
    """
    Convert SQL INSERT statement(s) to pandas DataFrame.
    
    Args:
        sql_text: SQL INSERT statement(s) as string
        
    Returns:
        pandas DataFrame
    """
    import json
    
    records = parse_sql_insert(sql_text)
    if not records:
        # Try to provide more helpful error message
        raise ValueError("No data extracted from SQL. Please ensure your SQL follows the format: INSERT INTO table_name (col1, col2) VALUES (val1, val2);")
    
    # Ensure all values are Excel-compatible
    safe_records = []
    for record in records:
        safe_record = {}
        for key, value in record.items():
            # Convert dict/list to JSON string
            if isinstance(value, (dict, list)):
                try:
                    safe_record[key] = json.dumps(value, ensure_ascii=False)
                except (TypeError, ValueError):
                    safe_record[key] = str(value)
            # Convert other non-standard types to string
            elif not isinstance(value, (str, int, float, type(None), bool)):
                safe_record[key] = str(value)
            else:
                safe_record[key] = value
        safe_records.append(safe_record)
    
    return pd.DataFrame(safe_records)


def save_sql_to_file(sql_text, file_format, output_folder, filename='sql_data'):
    """
    Save SQL data to file in specified format.
    
    Args:
        sql_text: SQL INSERT statement(s) as string
        file_format: Output format ('csv', 'xlsx', 'xls', 'md')
        output_folder: Directory to save output file
        filename: Base name for output file
        
    Returns:
        Path to saved file
    """
    df = sql_to_dataframe(sql_text)
    
    # Ensure all columns have Excel-compatible data types
    import unicodedata
    
    def sanitize_value(x):
        """Sanitize a single value for Excel compatibility."""
        import json
        
        # Convert dict/list to JSON string
        if isinstance(x, (dict, list)):
            try:
                return json.dumps(x, ensure_ascii=False)
            except (TypeError, ValueError):
                return str(x)
        
        # Convert to string if not a basic type
        if not isinstance(x, (str, int, float, type(None), bool)):
            x = str(x)
        
        # Clean string values
        if isinstance(x, str):
            # Remove zero-width and control characters except common ones
            cleaned = ''.join(
                char for char in x 
                if unicodedata.category(char)[0] != 'C' or char in '\n\r\t'
            )
            # Remove specific zero-width characters
            cleaned = cleaned.translate(str.maketrans('', '', '\u200b\u200c\u200d\ufeff'))
            return cleaned
        
        return x
    
    for col in df.columns:
        df[col] = df[col].apply(sanitize_value).astype(object)
    
    os.makedirs(output_folder, exist_ok=True)
    
    if file_format == 'csv':
        output_filename = f"{filename}.csv"
        output_path = os.path.join(output_folder, output_filename)
        df.to_csv(output_path, index=False, encoding='utf-8')
    elif file_format == 'xlsx':
        output_filename = f"{filename}.xlsx"
        output_path = os.path.join(output_folder, output_filename)
        df.to_excel(output_path, index=False, engine='openpyxl')
    elif file_format == 'xls':
        output_filename = f"{filename}.xls"
        output_path = os.path.join(output_folder, output_filename)
        df.to_excel(output_path, index=False, engine='xlwt')
    elif file_format == 'md':
        output_filename = f"{filename}.md"
        output_path = os.path.join(output_folder, output_filename)
        
        # Convert DataFrame to Markdown table
        md_content = df.to_markdown(index=False)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    else:
        raise ValueError(f"Unsupported output format: {file_format}")
    
    return output_path


def get_sql_preview(sql_text, max_rows=5):
    """
    Get a preview of SQL data as JSON-like structure.
    
    Args:
        sql_text: SQL INSERT statement(s) as string
        max_rows: Maximum number of rows to return
        
    Returns:
        Dictionary with preview data, columns, and total rows
    """
    records = parse_sql_insert(sql_text)
    
    if not records:
        return {"error": "No data extracted from SQL"}
    
    preview_data = records[:max_rows]
    
    # Get column names from first record
    if preview_data:
        columns = list(preview_data[0].keys())
    else:
        columns = []
    
    return {
        "preview": preview_data,
        "columns": columns,
        "total_rows": len(records)
    }

