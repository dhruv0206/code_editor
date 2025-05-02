import requests
import json

# Replace with your actual service URL
SERVICE_URL = "https://python-execution-api-843742829651.us-central1.run.app"

def test_cloud_api():
    url = f"{SERVICE_URL}/execute"
    headers = {"Content-Type": "application/json"}
    
    # Test script with pandas and numpy - NO LEADING SPACES before import statements
    script = """import pandas as pd
import numpy as np

def main():
    # Create a sample DataFrame
    df = pd.DataFrame({
        "A": np.random.rand(5),
        "B": np.random.rand(5)
    })
    
    print("DataFrame created successfully")
    print(df.head())
    
    return {
        "mean_A": float(df["A"].mean()),
        "mean_B": float(df["B"].mean())
    }
"""
    
    print(f"Testing API at: {url}")
    try:
        response = requests.post(url, headers=headers, json={"script": script}, timeout=30)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("\nSuccess! Response:")
            print(json.dumps(result, indent=2))
        else:
            print("\nError Response:")
            print(response.text)
    except Exception as e:
        print(f"Request failed: {str(e)}")

if __name__ == "__main__":
    test_cloud_api()