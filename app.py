import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from excel_processor.utils import read_file_to_dataframe

# Import your excel processing functions here
from excel_processor import (
    convert_column_to_list, 
    get_column_data, 
    convert_columns_to_json, 
    get_columns_as_json_records,
    add_json_column_to_file,
    convert_json_to_table,
    get_json_preview,
    process_clipboard_data_to_list,
    process_clipboard_json_to_table,
    save_clipboard_data_to_file,
    extract_lists_from_text,
    format_extracted_lists
)

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated_files'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
ALLOWED_SQL_EXTENSIONS = {'sql', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER
# Increase max content length to 50MB for large SQL files
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Ensure the upload and generated directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Global error handler to ensure JSON responses
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'Request too large. Please reduce the SQL content size (max 50MB).'}), 413

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request. Please check your input.'}), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error. Please try again.'}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tool/to-list')
def show_list_tool():
    return render_template('convert_list.html')

@app.route('/tool/to-json')
def show_json_tool():
    return render_template('convert_json.html')

@app.route('/tool/from-json')
def show_from_json_tool():
    return render_template('convert_from_json.html')

@app.route('/tool/clipboard')
def show_clipboard_tool():
    return render_template('process_clipboard.html')


@app.route('/convert/list', methods=['POST'])
def handle_list_conversion():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    column_name = request.form.get('column_name')
    output_method = request.form.get('output_method', 'file')

    if not column_name:
        return jsonify({'error': 'A column must be selected'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if output_method == 'file':
            output_path = convert_column_to_list(filepath, column_name, app.config['GENERATED_FOLDER'])
            if output_path:
                return jsonify({'download_url': f'/download/{os.path.basename(output_path)}'})
            else:
                return jsonify({'error': 'Failed to convert file.'}), 500
        
        elif output_method == 'display':
            try:
                column_data = get_column_data(filepath, column_name)
                # Convert data to a proper JSON array string for display
                data_list = [str(item) if item is not None and not pd.isna(item) else '' for item in column_data]
                json_string = '[' + ', '.join(data_list) + ']'
                return jsonify({'data': json_string, 'is_json_string': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        else:
            return jsonify({'error': 'Invalid output method'}), 400
            
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/get-headers', methods=['POST'])
def get_headers():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or no file selected'}), 400

    try:
        # Save to a temporary location to read it
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        df = read_file_to_dataframe(filepath)
        headers = df.columns.tolist()
        
        return jsonify({'headers': headers})
    except Exception as e:
        print(f"Error getting headers: {e}")
        return jsonify({'error': 'Could not process file. Please ensure it is a valid Excel or CSV file.'}), 500


@app.route('/convert/json', methods=['POST'])
def handle_json_conversion():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    column_names = request.form.getlist('column_names')
    output_method = request.form.get('output_method', 'file')
    
    if not column_names:
        return jsonify({'error': 'At least one column must be selected'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            if output_method == 'file':
                output_path = convert_columns_to_json(filepath, column_names, app.config['GENERATED_FOLDER'])
                if output_path:
                    return jsonify({'download_url': f'/download/{os.path.basename(output_path)}'})
            elif output_method == 'display':
                json_records = get_columns_as_json_records(filepath, column_names)
                return jsonify({'data': json_records})
            elif output_method == 'add_to_table':
                output_path = add_json_column_to_file(filepath, column_names, app.config['GENERATED_FOLDER'])
                if output_path:
                    return jsonify({'download_url': f'/download/{os.path.basename(output_path)}'})
            
            # If any path-based method failed, output_path would be None
            return jsonify({'error': 'Failed to process file.'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/convert/from-json', methods=['POST'])
def handle_from_json_conversion():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    output_format = request.form.get('output_format', 'csv')
    
    if file and file.filename.lower().endswith('.json'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            output_path = convert_json_to_table(filepath, output_format, app.config['GENERATED_FOLDER'])
            if output_path:
                return jsonify({'download_url': f'/download/{os.path.basename(output_path)}'})
            else:
                return jsonify({'error': 'Failed to convert JSON file.'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'File must be a JSON file'}), 400

@app.route('/convert/clipboard', methods=['POST'])
def handle_clipboard_conversion():
    data_text = request.form.get('data')
    action = request.form.get('action')
    
    if not data_text:
        return jsonify({'error': 'No data provided'}), 400
    
    if not action:
        return jsonify({'error': 'No action selected'}), 400
    
    try:
        if action == 'to_list':
            # Convert column to list
            output_method = request.form.get('list_output_method', 'display')
            
            if output_method == 'display':
                result = process_clipboard_data_to_list(data_text, 'display')
                return jsonify({'data': result, 'is_json_string': True})
            elif output_method == 'file':
                file_format = request.form.get('list_file_format', 'md')
                data_lines = process_clipboard_data_to_list(data_text, 'file')
                output_path = save_clipboard_data_to_file(data_lines, 'clipboard_data', file_format, app.config['GENERATED_FOLDER'])
                return jsonify({'download_url': f'/download/{os.path.basename(output_path)}'})
                
        elif action == 'from_json':
            # Convert JSON to table
            output_method = request.form.get('json_output_method', 'display')
            
            if output_method == 'display':
                result = process_clipboard_json_to_table(data_text, 'display')
                return jsonify({'data': result})
            elif output_method == 'file':
                file_format = request.form.get('json_file_format', 'csv')
                df = process_clipboard_json_to_table(data_text, file_format)
                output_path = save_clipboard_data_to_file(df, 'clipboard_data', file_format, app.config['GENERATED_FOLDER'])
                return jsonify({'download_url': f'/download/{os.path.basename(output_path)}'})
        
        elif action == 'extract_lists':
            # Extract lists from text
            output_method = request.form.get('extract_output_method', 'display')
            
            if output_method == 'display':
                result = extract_lists_from_text(data_text)
                formatted_result = format_extracted_lists(result)
                return jsonify({'data': formatted_result})
            elif output_method == 'file':
                file_format = request.form.get('extract_file_format', 'md')
                result = extract_lists_from_text(data_text)
                formatted_result = format_extracted_lists(result)
                # Save as text file
                output_filename = f"extracted_lists.md"
                output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)
                os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_result)
                return jsonify({'download_url': f'/download/{os.path.basename(output_path)}'})
        
        return jsonify({'error': 'Invalid action'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['GENERATED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
