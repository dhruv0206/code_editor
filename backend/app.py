# import json
# import os
# import subprocess
# import tempfile
# from flask import Flask, request, jsonify
# from flask_cors import CORS 

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# # CORS(app, resources={r"/*": {"origins": [
# #     "http://localhost:3000",
# #     "https://your-production-frontend-domain.com"
# # ]}})

# @app.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({"status": "ok"}), 200

# @app.route('/execute', methods=['POST'])
# def execute():
#     """Execute Python script"""
#     if not request.is_json:
#         return jsonify({"error": "Request body must be JSON"}), 400
    
#     data = request.get_json()
    
#     if 'script' not in data:
#         return jsonify({"error": "Missing 'script' field in request body"}), 400
    
#     script = data['script']
    
#     # For debugging, initially just run the script directly without nsjail
#     # Create a temporary file to store the script
#     with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
#         temp_file_path = temp_file.name
        
#         # Add wrapper to capture return value and stdout
#         wrapper_script = f'''
# import sys
# import json
# import io
# from contextlib import redirect_stdout

# # Original script
# {script}

# # Check if main function exists
# if 'main' not in globals() or not callable(globals()['main']):
#     sys.exit("Error: No main() function found in the script")

# # Capture stdout
# captured_output = io.StringIO()
# return_value = None

# try:
#     with redirect_stdout(captured_output):
#         return_value = main()
    
#     # Verify return value is JSON serializable
#     try:
#         json.dumps(return_value)
#     except (TypeError, OverflowError):
#         sys.exit("Error: main() function must return JSON serializable data")

#     # Print the result in a way we can parse later
#     print("RETURN_VALUE_MARKER")
#     print(json.dumps(return_value))
#     print("STDOUT_MARKER")
#     print(captured_output.getvalue())
    
# except Exception as e:
#     import traceback
#     sys.exit(f"Error during execution: {{str(e)}}\\n{{traceback.format_exc()}}")
# '''
#         temp_file.write(wrapper_script.encode())

#     try:
#         # Direct execution without nsjail for initial testing
#         process = subprocess.run(
#             ["python", temp_file_path],
#             capture_output=True,
#             text=True,
#             timeout=30
#         )
        
#         # Clean up temporary file
#         try:
#             os.unlink(temp_file_path)
#         except:
#             pass
        
#         if process.returncode != 0:
#             return jsonify({
#                 "error": f"Execution failed with exit code {process.returncode}",
#                 "stdout": process.stdout,
#                 "stderr": process.stderr
#             }), 400
        
#         # Parse output to separate return value and stdout
#         output = process.stdout
#         return_value_part = None
#         stdout_part = ""
        
#         if "RETURN_VALUE_MARKER" in output and "STDOUT_MARKER" in output:
#             parts = output.split("RETURN_VALUE_MARKER")
#             if len(parts) > 1:
#                 value_and_stdout = parts[1].split("STDOUT_MARKER")
#                 if len(value_and_stdout) > 1:
#                     return_value_part = value_and_stdout[0].strip()
#                     stdout_part = value_and_stdout[1].strip()
        
#         if return_value_part:
#             try:
#                 return_value = json.loads(return_value_part)
#                 return jsonify({
#                     "result": return_value,
#                     "stdout": stdout_part
#                 }), 200
#             except json.JSONDecodeError:
#                 return jsonify({
#                     "error": "Failed to parse return value as JSON",
#                     "stdout": stdout_part
#                 }), 400
#         else:
#             return jsonify({
#                 "error": "Couldn't extract return value from script execution",
#                 "stdout": output
#             }), 400
            
#     except subprocess.TimeoutExpired:
#         return jsonify({
#             "error": "Script execution timed out",
#             "stdout": ""
#         }), 400
#     except Exception as e:
#         return jsonify({
#             "error": f"Error running script: {str(e)}",
#             "stdout": ""
#         }), 500

# if __name__ == '__main__':
#     print("Starting Flask application...")
#     app.run(host='0.0.0.0', port=8080, debug=True)






import json
import os
import subprocess
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS 

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

@app.route('/execute', methods=['POST'])
def execute():
    """Execute Python script with strict type validation"""
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    data = request.get_json()
    
    if 'script' not in data:
        return jsonify({"error": "Missing 'script' field in request body"}), 400
    
    script = data['script']
    
    # Create a temporary file to store the script
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
        temp_file_path = temp_file.name
        
        # Add wrapper with explicit type validation
        wrapper_script = f'''
import sys
import json
import io
from contextlib import redirect_stdout

# Original script
{script}

# Check if main function exists
if 'main' not in globals() or not callable(globals()['main']):
    sys.exit("Error: No main() function found in the script")

# Capture stdout
captured_output = io.StringIO()

try:
    with redirect_stdout(captured_output):
        return_value = main()
    
    # STRICT TYPE VALIDATION: Only accept dict or list as valid return types
    if not isinstance(return_value, dict) and not isinstance(return_value, list):
        # This is the critical validation - explicitly check for dict OR list
        sys.exit(f"Error: main() function must return a JSON object. Got {{type(return_value).__name__}} instead: {{repr(return_value)}}")
    
    # If we got here, try to serialize to JSON
    try:
        json_result = json.dumps(return_value)
    except Exception as e:
        sys.exit(f"Error: Could not convert return value to JSON: {{str(e)}}")
    
    # Print the result
    print("RETURN_VALUE_MARKER")
    print(json_result)
    print("STDOUT_MARKER")
    print(captured_output.getvalue())
    
except Exception as e:
    import traceback
    sys.exit(f"Error during execution: {{str(e)}}\\n{{traceback.format_exc()}}")
'''
        temp_file.write(wrapper_script.encode())

    try:
        # Execute the script
        process = subprocess.run(
            ["python", temp_file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass
        
        # Check if the script execution failed
        if process.returncode != 0:
            # Return the error message
            return jsonify({
                "error": process.stderr.strip(),
                "stdout": process.stdout
            }), 400
        
        # Process successful execution
        output = process.stdout
        if "RETURN_VALUE_MARKER" not in output or "STDOUT_MARKER" not in output:
            return jsonify({
                "error": "Invalid script output format",
                "stdout": output
            }), 400
        
        # Extract return value and stdout
        parts = output.split("RETURN_VALUE_MARKER")
        value_and_stdout = parts[1].split("STDOUT_MARKER")
        return_value_json = value_and_stdout[0].strip()
        stdout_content = value_and_stdout[1].strip()
        
        # Parse the JSON
        try:
            return_value = json.loads(return_value_json)
            
            # Double-check the type again on the server side
            if not isinstance(return_value, (dict, list)):
                return jsonify({
                    "error": f"Server validation failed: Result must be a JSON object (dict) or array (list), received: {type(return_value).__name__}",
                    "stdout": stdout_content
                }), 400
                
            # Return the successful result
            return jsonify({
                "result": return_value,
                "stdout": stdout_content
            }), 200
            
        except json.JSONDecodeError as e:
            return jsonify({
                "error": f"Failed to parse return value as JSON: {str(e)}",
                "stdout": stdout_content
            }), 400
            
    except subprocess.TimeoutExpired:
        return jsonify({
            "error": "Script execution timed out",
            "stdout": ""
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Error running script: {str(e)}",
            "stdout": ""
        }), 500

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=8080, debug=True)