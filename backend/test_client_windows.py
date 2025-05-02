# import requests
# import json
# import time
# import sys

# BASE_URL = "http://localhost:8080"

# def run_test(test_name, script):
#     """Run a test against the API"""
#     print(f"\n{'=' * 40}")
#     print(f"Running test: {test_name}")
#     print(f"{'=' * 40}")
    
#     try:
#         response = requests.post(
#             f"{BASE_URL}/execute", 
#             json={"script": script},
#             timeout=30
#         )
        
#         print(f"Status Code: {response.status_code}")
        
#         if response.status_code == 200:
#             result = response.json()
#             print("\nRESULT:")
#             print(json.dumps(result["result"], indent=2))
            
#             if result["stdout"]:
#                 print("\nSTDOUT:")
#                 print(result["stdout"])
#         else:
#             try:
#                 error = response.json().get("error", "Unknown error")
#                 stdout = response.json().get("stdout", "")
#                 print(f"Error: {error}")
#                 if stdout:
#                     print(f"Stdout: {stdout}")
#             except:
#                 print(f"Raw response: {response.text}")
    
#     except Exception as e:
#         print(f"Failed to connect: {str(e)}")
    
#     print("\n")

# def run_all_tests():
#     """Run all test cases"""
    
#     # First check if the server is running
#     try:
#         health_response = requests.get(f"{BASE_URL}/health", timeout=5)
#         if health_response.status_code != 200:
#             print(f"Server health check failed with status code: {health_response.status_code}")
#             return
#     except Exception as e:
#         print(f"Server not running or not reachable: {str(e)}")
#         print("Please make sure Docker is running and the container is started")
#         return
    
#     print("Server is running! Starting tests...\n")
    
#     # Test 1: Basic script
#     run_test("Basic Script", """
# def main():
#     return {"message": "Hello from Windows!"}
# """)

#     # Test 2: Using pandas and numpy
#     run_test("Using Pandas and NumPy", """
# import pandas as pd
# import numpy as np

# def main():
#     # Create a sample dataframe
#     df = pd.DataFrame({
#         "A": np.random.rand(5),
#         "B": np.random.rand(5)
#     })
    
#     # Print to stdout
#     print("DataFrame created with shape:", df.shape)
    
#     # Return a result
#     return {
#         "mean_A": float(df["A"].mean()),
#         "mean_B": float(df["B"].mean()),
#         "correlation": float(df["A"].corr(df["B"]))
#     }
# """)

#     # Test 3: Script with syntax error
#     run_test("Syntax Error", """
# def main()
#     return {"message": "Hello, World!"}
# """)

#     # Test 4: Script with runtime error
#     run_test("Runtime Error", """
# def main():
#     # This will cause a division by zero error
#     x = 1 / 0
#     return {"result": x}
# """)

# if __name__ == "__main__":
#     print("Python Execution API Tester for Windows")
#     print("---------------------------------------")
    
#     # Wait a bit for server to fully start up
#     if len(sys.argv) > 1 and sys.argv[1] == "--wait":
#         print("Waiting 10 seconds for server to start...")
#         time.sleep(10)
    
#     run_all_tests()

import requests
import json
import time

def test_api(script, test_name):
    print(f"\n==== Testing: {test_name} ====")
    
    url = "http://localhost:8080/execute"
    headers = {"Content-Type": "application/json"}
    data = {"script": script}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nResult:")
            print(json.dumps(result, indent=2))
        else:
            print("\nError Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
    
    except Exception as e:
        print(f"Request failed: {str(e)}")

if __name__ == "__main__":
    # Test 1: Simple script
    test_api(
        """def main():
    return {"message": "Hello from Windows!"}""",
        "Simple Script"
    )
    
    time.sleep(1)  # Add a small delay between requests
    
    # Test 2: With pandas and numpy
    test_api(
        """import pandas as pd
import numpy as np

def main():
    # Create a sample dataframe
    df = pd.DataFrame({
        "A": np.random.rand(5),
        "B": np.random.rand(5)
    })
    
    print("DataFrame created successfully")
    
    return {
        "mean_A": float(df["A"].mean()),
        "mean_B": float(df["B"].mean())
    }""",
        "Pandas and NumPy"
    )