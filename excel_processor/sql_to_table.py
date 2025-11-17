import pandas as pd
import re
import os
from io import StringIO


def parse_create_table(sql_text):
    """
    Parses a CREATE TABLE statement to extract column names.
    Returns a dictionary mapping table name to a list of column names.
    """
    create_table_pattern = re.compile(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\((.*?)\);',
        re.IGNORECASE | re.DOTALL
    )
    
    tables = {}
    match = create_table_pattern.search(sql_text)
    if not match:
        return tables

    table_name = match.group(1)
    columns_str = match.group(2)
    
    # Remove comments inside create table statement
    columns_str = re.sub(r'--.*?$', '', columns_str, flags=re.MULTILINE)
    
    # Extract column names, which are typically enclosed in backticks
    column_pattern = re.compile(r'^\s*`(\w+)`', re.MULTILINE)
    columns = column_pattern.findall(columns_str)
    
    if columns:
        tables[table_name] = columns
            
    return tables

def parse_sql_insert(sql_text):
    """
    Parse SQL INSERT statements and extract data into a list of dictionaries.
    Supports single and multiple INSERT statements, and statements with or without column names.
    Handles complex strings with escaped quotes.
    Extracts column headers from CREATE TABLE statements if present.
    """
    # Remove comments
    sql_text = re.sub(r'--.*?$', '', sql_text, flags=re.MULTILINE)
    sql_text = re.sub(r'/\*.*?\*/', '', sql_text, flags=re.DOTALL)
    
    table_schemas = parse_create_table(sql_text)
    all_records = []
    
    # Regex to find all INSERT statements
    insert_pattern = re.compile(r'INSERT\s+INTO\s+`?(\w+)`?(?:\s*\((.*?)\))?\s+VALUES\s*(.*?);', re.IGNORECASE | re.DOTALL)
    
    for match in insert_pattern.finditer(sql_text):
        table_name, columns_str, values_section = match.groups()

        columns = []
        if columns_str:
            columns = [col.strip().strip('`"') for col in columns_str.split(',')]
        elif table_name in table_schemas:
            columns = table_schemas[table_name]

        # Extract value groups: (val1, val2), (val3, val4)
        value_groups_str = values_section.strip()
        
        # Correctly parse multiple value tuples
        if value_groups_str.startswith('('):
            # Split records, handling the case of `), (`
            records_str = re.split(r'\)\s*,\s*\(', value_groups_str)
            # Clean up first and last elements
            if records_str:
                records_str[0] = records_str[0][1:]
                records_str[-1] = records_str[-1][:-1]
        else:
            records_str = []

        for record_str in records_str:
            values = parse_values(record_str)
            
            # If columns are still not determined, infer from the first row
            if not columns:
                columns = [f'column_{i+1}' for i in range(len(values))]
                if table_name not in table_schemas:
                    table_schemas[table_name] = columns

            if len(values) == len(columns):
                record = dict(zip(columns, values))
                all_records.append(record)
            else:
                # Handle mismatch, pad with None or truncate
                if len(values) < len(columns):
                    values.extend([None] * (len(columns) - len(values)))
                else:
                    values = values[:len(columns)]
                record = dict(zip(columns, values))
                all_records.append(record)

    return all_records

def parse_values(value_string):
    """Parse a comma-separated list of values, respecting quoted strings and escaped characters."""
    values = []
    i = 0
    current_value = ""
    while i < len(value_string):
        # Find the start of the next value
        trimmed_val_str = value_string[i:].lstrip()
        i = len(value_string) - len(trimmed_val_str)
        
        if not trimmed_val_str:
            break

        if trimmed_val_str.upper().startswith('NULL'):
            values.append(None)
            i += 4
            # Move past comma
            next_comma = value_string.find(',', i)
            if next_comma != -1:
                i = next_comma + 1
            else:
                i = len(value_string)
            continue
        
        if trimmed_val_str.startswith("'") or trimmed_val_str.startswith('"'):
            quote_char = trimmed_val_str[0]
            end_quote_idx = -1
            search_start = i + 1
            while True:
                end_quote_idx = value_string.find(quote_char, search_start)
                if end_quote_idx == -1:
                    # Unterminated string
                    break
                # Check for escaped quote
                if value_string[end_quote_idx-1] == '\\':
                    search_start = end_quote_idx + 1
                    continue
                # For SQL, quotes are escaped by doubling them e.g. ''
                if (end_quote_idx + 1 < len(value_string)) and (value_string[end_quote_idx+1] == quote_char):
                    search_start = end_quote_idx + 2
                    continue
                break
            
            if end_quote_idx != -1:
                value = value_string[i+1:end_quote_idx]
                values.append(clean_value(f"{quote_char}{value}{quote_char}"))
                i = end_quote_idx + 1
            else:
                # Add the rest as a value and break
                values.append(clean_value(value_string[i:]))
                break
        else:
            # Numeric or other unquoted value
            next_comma = value_string.find(',', i)
            if next_comma != -1:
                value = value_string[i:next_comma].strip()
                values.append(clean_value(value))
                i = next_comma + 1
            else:
                value = value_string[i:].strip()
                values.append(clean_value(value))
                break # Last value
                
        # Move past comma
        next_comma = value_string.find(',', i)
        if next_comma != -1:
            i = next_comma + 1
        else:
            break

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

