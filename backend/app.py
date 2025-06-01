import json
import os
import subprocess
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS 

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


NSJAIL_BINARY = "/usr/bin/nsjail"  
NSJAIL_CONFIG = "./nsjail.config"  

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

def check_nsjail_available():
    """Check if nsjail is available and config exists"""
    if not os.path.exists(NSJAIL_BINARY):
        raise FileNotFoundError(f"nsjail binary not found at {NSJAIL_BINARY}")
    if not os.path.exists(NSJAIL_CONFIG):
        raise FileNotFoundError(f"nsjail config not found at {NSJAIL_CONFIG}")

# This endpoint is for debugging purposes

# @app.route('/debug', methods=['GET'])
# def debug_nsjail():
#     """Debug endpoint to test nsjail setup"""
#     try:
#         check_nsjail_available()
#     except FileNotFoundError as e:
#         return jsonify({"error": f"Sandbox not available: {str(e)}"}), 500
    
#     # Test basic nsjail execution
#     try:
#         # Test 1: Check if we can run anything
#         test_command = [
#             NSJAIL_BINARY,
#             "--config", NSJAIL_CONFIG,
#             "--",
#             "echo", "Hello from nsjail"
#         ]
        
#         process = subprocess.run(
#             test_command,
#             capture_output=True,
#             text=True,
#             timeout=10
#         )
        
#         echo_result = {
#             "returncode": process.returncode,
#             "stdout": process.stdout,
#             "stderr": process.stderr
#         }
        
#         # Test 2: Check available Python versions and paths
#         python_test_command = [
#             NSJAIL_BINARY,
#             "--config", NSJAIL_CONFIG,
#             "--",
#             "sh", "-c", """
#             echo "=== Which commands ==="
#             which python 2>/dev/null || echo "python not found"
#             which python3 2>/dev/null || echo "python3 not found" 
#             echo "=== Listing python executables ==="
#             ls -la /usr/bin/python* 2>/dev/null || echo "No python in /usr/bin"
#             ls -la /usr/local/bin/python* 2>/dev/null || echo "No python in /usr/local/bin"
#             ls -la /bin/python* 2>/dev/null || echo "No python in /bin"
#             echo "=== PATH ==="
#             echo $PATH
#             echo "=== Find python ==="
#             find /usr -name "python*" -type f 2>/dev/null | head -5 || echo "Find failed"
#             """
#         ]
        
#         python_process = subprocess.run(
#             python_test_command,
#             capture_output=True,
#             text=True,
#             timeout=10
#         )
        
#         python_result = {
#             "returncode": python_process.returncode,
#             "stdout": python_process.stdout,
#             "stderr": python_process.stderr
#         }
        
#         # Test 3: Try to run Python directly
#         direct_python_command = [
#             NSJAIL_BINARY,
#             "--config", NSJAIL_CONFIG,
#             "--",
#             "/usr/local/bin/python3", "-c", "import sys; print('Python version:', sys.version); print('Executable:', sys.executable)"
#         ]
        
#         direct_process = subprocess.run(
#             direct_python_command,
#             capture_output=True,
#             text=True,
#             timeout=10
#         )
        
#         direct_result = {
#             "returncode": direct_process.returncode,
#             "stdout": direct_process.stdout,
#             "stderr": direct_process.stderr
#         }
        
#         return jsonify({
#             "echo_test": echo_result,
#             "python_discovery": python_result,
#             "direct_python_test": direct_result
#         })
        
#     except Exception as e:
#         return jsonify({"error": f"Debug test failed: {str(e)}"}), 500



def find_python_executable():
    """Find the best Python executable to use in nsjail"""
    python_candidates = [
        "/usr/local/bin/python3",
        "/usr/local/bin/python",
        "/usr/bin/python3",
        "/usr/bin/python",
        "/bin/python3",
        "/bin/python",
        "python3",
        "python"
    ]
    
    for python_cmd in python_candidates:
        try:
            test_command = [
                NSJAIL_BINARY,
                "--config", NSJAIL_CONFIG,
                "--",
                python_cmd, "-c", "print('test')"
            ]
            
            process = subprocess.run(
                test_command,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if process.returncode == 0 and "test" in process.stdout:
                print(f"✓ Found working Python executable: {python_cmd}")
                return python_cmd
            else:
                print(f"✗ Python executable {python_cmd} failed:")
                print(f"  Return code: {process.returncode}")
                print(f"  Stdout: {process.stdout}")
                print(f"  Stderr: {process.stderr}")
                
        except Exception as e:
            print(f"✗ Exception testing {python_cmd}: {e}")
            continue
    
    return None

@app.route('/execute', methods=['POST'])
def execute():
    """Execute Python script with strict type validation using nsjail"""
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    data = request.get_json()
    
    if 'script' not in data:
        return jsonify({"error": "Missing 'script' field in request body"}), 400
    
    script = data['script']
    
    # Check if nsjail is available
    try:
        check_nsjail_available()
    except FileNotFoundError as e:
        return jsonify({"error": f"Sandbox not available: {str(e)}"}), 500
    
    # Find working Python executable
    python_executable = find_python_executable()
    if not python_executable:
        return jsonify({"error": "No working Python executable found in sandbox"}), 500
    
    # Create a temporary file to store the script
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_file:
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
        temp_file.write(wrapper_script)

    try:
        # Execute the script using nsjail with the found Python executable
        nsjail_command = [
            NSJAIL_BINARY,
            "--config", NSJAIL_CONFIG,
            "--",
            python_executable, temp_file_path
        ]
        
        process = subprocess.run(
            nsjail_command,
            capture_output=True,
            text=True,
            timeout=35  # Slightly longer than nsjail's internal timeout
        )
        
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass
        
        # Check if the script execution failed
        if process.returncode != 0:
            # Parse nsjail-specific errors
            stderr = process.stderr.strip()
            stdout = process.stdout.strip()
            
            # Check for common nsjail termination reasons
            if "TIMEOUT" in stderr or "time limit exceeded" in stderr.lower():
                return jsonify({
                    "error": "Script execution timed out (30 seconds limit)",
                    "stdout": stdout
                }), 400
            elif "MEMORY" in stderr or "memory limit" in stderr.lower():
                return jsonify({
                    "error": "Script exceeded memory limit",
                    "stdout": stdout
                }), 400
            elif "CPU" in stderr or "cpu limit" in stderr.lower():
                return jsonify({
                    "error": "Script exceeded CPU limit",
                    "stdout": stdout
                }), 400
            elif process.returncode == 127:
                return jsonify({
                    "error": f"Python executable not found: {python_executable}",
                    "stdout": stdout
                }), 400
            else:
                # Return the error message from the script
                return jsonify({
                    "error": stderr if stderr else stdout if stdout else "Script execution failed",
                    "stdout": stdout
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
            "error": "Script execution timed out at system level",
            "stdout": ""
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Error running script: {str(e)}",
            "stdout": ""
        }), 500

if __name__ == '__main__':
    print("Starting Flask application...")
    print(f"Using nsjail binary: {NSJAIL_BINARY}")
    print(f"Using nsjail config: {NSJAIL_CONFIG}")
    
    # Show host system Python info
    print("\n=== Host System Python Info ===")
    import sys
    print(f"Host Python executable: {sys.executable}")
    print(f"Host Python version: {sys.version}")
    
    # Verify nsjail is available at startup
    try:
        check_nsjail_available()
        print("✓ nsjail sandbox is available")
        
        # Test Python executable
        python_exe = find_python_executable()
        if python_exe:
            print(f"✓ Found working Python executable: {python_exe}")
        else:
            print("⚠ Warning: No working Python executable found in sandbox!")
            print("Try the /debug endpoint to see what's available in the sandbox")
            
    except FileNotFoundError as e:
        print(f"⚠ Warning: {e}")
        print("Scripts will not be sandboxed!")
    
    app.run(host='0.0.0.0', port=8080, debug=True)