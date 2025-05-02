Write-Host "Building Docker image..." -ForegroundColor Green
docker build -t python-execution-api .

Write-Host "Running container..." -ForegroundColor Green
docker run -p 8080:8080 python-execution-api