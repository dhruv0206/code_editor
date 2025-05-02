# Python Code Execution API with React Frontend

This project consists of a backend API for securely executing Python code in a sandboxed environment and a React-based frontend for interacting with the API.

## Features

### Backend

- Executes Python code in a secure sandbox using `nsjail`.
- Captures the return value from the `main()` function and standard output (`stdout`) separately.
- Enforces resource limits (CPU, memory, execution time).
- Provides error handling for invalid Python syntax, missing `main()` function, and non-JSON-serializable return values.

### Frontend

- A React-based web interface with a code editor powered by `react-ace`.
- Allows users to write Python code, execute it, and view the results and standard output.
- Displays errors in a user-friendly manner.

---

## Project Structure

```
.
├── backend/                # Backend API for Python code execution
│   ├── app.py              # Flask application for handling API requests
│   ├── dockerfile          # Dockerfile for building the backend container
│   ├── requirements.txt    # Python dependencies
│   ├── nsjail.config.proto # Configuration for nsjail sandbox
│   ├── test_cloud.py       # Script for testing the backend API
│   └── run_windows.ps1     # Script for running the backend on Windows
├── frontend/               # React-based frontend
│   ├── src/                # Source code for the React app
│   │   ├── components/     # React components
│   │   │   └── CodeEditor.js # Code editor component
│   │   ├── App.js          # Main React component
│   │   ├── index.js        # Entry point for the React app
│   │   └── index.css       # Tailwind CSS styles
│   ├── public/             # Static assets
│   ├── dockerfile          # Dockerfile for building the frontend container
│   ├── nginx.conf          # Nginx configuration for serving the frontend
│   └── package.json        # Frontend dependencies and scripts
├── docker-compose.yml      # Docker Compose configuration for running the project
└── README.md               # Project documentation
```

---

## Getting Started

### Prerequisites

- Docker
- Node.js (for local frontend development)
- Python 3.9+ (for local backend development)

---

### Running Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. Start the services using Docker Compose:

   ```bash
   docker-compose up
   ```

3. Access the frontend at [http://localhost:3000](http://localhost:3000).
4. The backend API will be available at [http://localhost:8080](http://localhost:8080).

---

## Example cURL Requests

### Simple Hello World

```bash
curl -X POST https://python-execution-api-843742829651.us-central1.run.app/execute -H "Content-Type: application/json" -d "{\"script\": \"def main():\n    return {\\\"message\\\": \\\"Hello from CMD!\\\"}\"}"
```

### Using Pandas and NumPy

```bash
curl -X POST https://python-execution-api-843742829651.us-central1.run.app/execute -H "Content-Type: application/json" -d "{\"script\": \"import pandas as pd\nimport numpy as np\n\ndef main():\n    df = pd.DataFrame({\\\"A\\\": [1, 2, 3], \\\"B\\\": [4, 5, 6]})\n    print(df)\n    return {\\\"sum\\\": int(df.sum().sum())}\"}"
```

### Using Pandas and NumPy with Random Data

```bash
curl -X POST https://python-execution-api-843742829651.us-central1.run.app/execute -H "Content-Type: application/json" -d "{\"script\": \"import pandas as pd\nimport numpy as np\n\ndef main():\n    # Create a sample DataFrame\n    df = pd.DataFrame({\n        \\\"A\\\": np.random.rand(5),\n        \\\"B\\\": np.random.rand(5)\n    })\n    \n    print(\\\"DataFrame created successfully\\\")\n    print(df.head())\n    \n    return {\n        \\\"mean_A\\\": float(df[\\\"A\\\"].mean()),\n        \\\"mean_B\\\": float(df[\\\"B\\\"].mean())\n    }\"}"
```

---

## Deployment

### Backend Deployment to Google Cloud Run

1. Build and push the Docker image:

   ```bash
   gcloud builds submit --tag gcr.io/your-project-id/python-execution-api
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy python-execution-api \
     --image gcr.io/your-project-id/python-execution-api \
     --platform managed \
     --allow-unauthenticated
   ```

### Frontend Deployment

1. Build the frontend:

   ```bash
   cd frontend
   npm run build
   ```

2. Deploy the built files to a static hosting service or integrate with the backend's Nginx configuration.

---

## Security Considerations

- The backend uses `nsjail` to sandbox Python code execution, ensuring process isolation and resource limits.
- Network access is restricted, and only essential libraries are available in the sandbox.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
