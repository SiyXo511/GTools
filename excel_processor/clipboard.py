import pandas as pd
import os
import json
import io

def dataframe_to_markdown(df):
    """
    Convert DataFrame to Markdown table format without external dependencies.
    """
    if df.empty:
        return ""
    
    # Get column names
    columns = df.columns.tolist()
    
    # Create header row
    header = "| " + " | ".join(str(col) for col in columns) + " |"
    
    # Create separator row
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    
    # Create data rows
    rows = []
    for _, row in df.iterrows():
        row_data = "| " + " | ".join(str(cell) if pd.notna(cell) else "" for cell in row) + " |"
        rows.append(row_data)
    
    # Combine all parts
    markdown_table = [header, separator] + rows
    return "\n".join(markdown_table)

def process_clipboard_data_to_list(data_text, output_format='display'):
    """
    Process clipboard data and convert to list format.
    Supports both display and file output.
    """
    try:
        # Split the text into lines and clean up
        lines = [line.strip() for line in data_text.strip().split('\n') if line.strip()]
        
        if not lines:
            raise ValueError("No data found in clipboard")
        
        # Convert to list format
        if output_format == 'display':
            # Return as comma-separated list string
            return '[' + ', '.join(lines) + ']'
        elif output_format == 'file':
            # Return the lines for file writing
            return lines
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
    except Exception as e:
        raise ValueError(f"Error processing clipboard data: {str(e)}")

def process_clipboard_json_to_table(data_text, output_format='csv'):
    """
    Process clipboard JSON data and convert to table format.
    """
    try:
        # Parse JSON data
        json_data = json.loads(data_text)
        
        if not isinstance(json_data, list):
            raise ValueError("JSON data must be a list of objects")
        
        if len(json_data) == 0:
            raise ValueError("JSON data is empty")
        
        # Convert to DataFrame
        df = pd.DataFrame(json_data)
        
        if output_format == 'display':
            # Return as CSV string for display
            return df.to_csv(index=False)
        elif output_format in ['csv', 'xlsx', 'xls']:
            # Return DataFrame for file writing
            return df
        elif output_format == 'md':
            # Convert to Markdown table manually
            return dataframe_to_markdown(df)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing JSON data: {str(e)}")

def extract_lists_from_text(text):
    """
    Extract all lists (content within []) from text.
    Returns a dictionary with:
    - combined_list: A merged list of all items from all lists
    - individual_lists: A list of individual extracted lists
    """
    import re
    import json
    
    # Pattern to match content within square brackets, handling nested brackets
    # This regex matches [ ... ] but handles nested brackets correctly
    lists = []
    depth = 0
    start_idx = -1
    
    i = 0
    while i < len(text):
        if text[i] == '[':
            if depth == 0:
                start_idx = i + 1  # Start after the opening bracket
            depth += 1
        elif text[i] == ']':
            depth -= 1
            if depth == 0 and start_idx != -1:
                # Extract the content between brackets
                content = text[start_idx:i].strip()
                if content:
                    lists.append(content)
                start_idx = -1
        i += 1
    
    # Parse each extracted list content
    individual_lists = []
    combined_items = []
    
    for list_content in lists:
        # Try to parse as JSON array first
        try:
            # Try wrapping in brackets to make it a valid JSON array
            json_str = '[' + list_content + ']'
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                individual_lists.append(parsed)
                combined_items.extend(parsed)
                continue
        except (json.JSONDecodeError, ValueError):
            pass
        
        # If JSON parsing fails, try comma-separated values
        # Split by comma, but be careful with quotes
        items = []
        current_item = ""
        in_quotes = False
        quote_char = None
        
        for char in list_content:
            if char in ['"', "'"] and (not current_item or current_item[-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                    current_item += char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                    current_item += char
                else:
                    current_item += char
            elif char == ',' and not in_quotes:
                if current_item.strip():
                    items.append(current_item.strip())
                current_item = ""
            else:
                current_item += char
        
        # Add the last item
        if current_item.strip():
            items.append(current_item.strip())
        
        if items:
            individual_lists.append(items)
            combined_items.extend(items)
    
    return {
        'combined_list': combined_items,
        'individual_lists': individual_lists
    }


def format_extracted_lists(result):
    """
    Format extracted lists result for display.
    First line: combined list as JSON array
    Following lines: each individual list
    """
    output_lines = []
    
    # First line: combined list
    import json
    combined_json = json.dumps(result['combined_list'], ensure_ascii=False)
    output_lines.append(combined_json)
    
    # Following lines: individual lists
    for i, individual_list in enumerate(result['individual_lists'], 1):
        list_json = json.dumps(individual_list, ensure_ascii=False)
        output_lines.append(f"\n列表 {i}: {list_json}")
    
    return '\n'.join(output_lines)


def save_clipboard_data_to_file(data, filename, output_format, output_folder):
    """
    Save processed clipboard data to file.
    """
    try:
        base_name = os.path.splitext(filename)[0]
        
        if output_format == 'md':
            output_filename = f"{base_name}_clipboard.md"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                if isinstance(data, list):
                    # For list data, create comma-separated list format
                    f.write('[' + ', '.join(data) + ']')
                else:
                    # For DataFrame, write as markdown table
                    f.write(data)
            
        elif output_format == 'csv':
            output_filename = f"{base_name}_clipboard.csv"
            output_path = os.path.join(output_folder, output_filename)
            data.to_csv(output_path, index=False, encoding='utf-8')
            
        elif output_format in ['xlsx', 'xls']:
            output_filename = f"{base_name}_clipboard.{output_format}"
            output_path = os.path.join(output_folder, output_filename)
            data.to_excel(output_path, index=False)
            
        else:
            raise ValueError(f"Unsupported file format: {output_format}")
        
        return output_path
        
    except Exception as e:
        raise ValueError(f"Error saving file: {str(e)}")
