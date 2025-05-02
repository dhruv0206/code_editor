import React, { useState } from "react";
import AceEditor from "react-ace";
import axios from "axios";

// Import ace modes and themes
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";

const CodeEditor = () => {
  const [code, setCode] = useState(
    `import pandas as pd
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
`
  );
  const [result, setResult] = useState(null);
  const [stdout, setStdout] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCodeChange = (newCode) => {
    setCode(newCode);
  };

  const executeCode = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setStdout("");

    try {
      // Replace with your actual Cloud Run service URL
      const apiUrl =
        "https://python-execution-api-843742829651.us-central1.run.app/execute";

      const response = await axios.post(apiUrl, {
        script: code,
      });

      setResult(response.data.result);
      setStdout(response.data.stdout);
    } catch (err) {
      console.error("Execution error:", err);
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Python Code Execution
      </h1>

      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
        <div className="bg-gray-800 text-white px-4 py-3">
          <h2 className="text-lg font-semibold">Code Editor</h2>
        </div>
        <div className="border border-gray-200">
          <AceEditor
            mode="python"
            theme="monokai"
            name="codeEditor"
            value={code}
            onChange={handleCodeChange}
            fontSize={14}
            width="100%"
            height="400px"
            showPrintMargin={true}
            showGutter={true}
            highlightActiveLine={true}
            setOptions={{
              enableBasicAutocompletion: true,
              enableLiveAutocompletion: true,
              enableSnippets: true,
              showLineNumbers: true,
              tabSize: 4,
            }}
          />
        </div>
        <div className="px-4 py-3 bg-gray-100">
          <button
            className={`px-4 py-2 rounded-md text-white ${
              loading
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
            onClick={executeCode}
            disabled={loading}
          >
            {loading ? "Executing..." : "Run Code"}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6">
          <h3 className="font-bold">Error:</h3>
          <pre className="mt-2 whitespace-pre-wrap">{error}</pre>
        </div>
      )}

      {stdout && (
        <div className="bg-white shadow-md rounded-lg overflow-hidden mb-6">
          <div className="bg-gray-800 text-white px-4 py-3">
            <h2 className="text-lg font-semibold">Standard Output</h2>
          </div>
          <div className="p-4">
            <pre className="whitespace-pre-wrap font-mono text-sm">
              {stdout}
            </pre>
          </div>
        </div>
      )}

      {result && (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <div className="bg-gray-800 text-white px-4 py-3">
            <h2 className="text-lg font-semibold">Result</h2>
          </div>
          <div className="p-4">
            <pre className="whitespace-pre-wrap font-mono text-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeEditor;
