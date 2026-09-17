<#
.SYNOPSIS
Scaffolds a complete Kubernetes API lab for Kubeshark traffic testing.

.DESCRIPTION
This script generates a folder structure containing a Python Flask API, 
a Dockerfile for building the image locally in Minikube, and Kubernetes 
YAML manifests (Deployment and Service) to test Kubeshark traffic monitoring.
#>

$LabName = "kubeshark-traffic-lab"
$AppDir = "$LabName\app"
$K8sDir = "$LabName\k8s"

Write-Host "🚀 Scaffolding Kubeshark Traffic Lab..." -ForegroundColor Cyan

# 1. Create Directory Structure
New-Item -ItemType Directory -Force -Path $AppDir | Out-Null
New-Item -ItemType Directory -Force -Path $K8sDir | Out-Null
Write-Host "✅ Created folder structure: $LabName" -ForegroundColor Green

# 2. Create Python API (server.py) with Mock Data
$PythonCode = @"
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# Mock data for Kubeshark to intercept
MOCK_DATA = {
    "status": "success",
    "metrics": {
        "cpu_usage": "45%",
        "memory_usage": "1.2GB",
        "active_connections": 154
    },
    "user_session": {
        "user_id": "usr_9824xyz",
        "role": "admin",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('X-App-Version', 'v1.0.0')
        self.end_headers()
        
        # When Kubeshark taps this, you will see this rich JSON payload
        self.wfile.write(json.dumps(MOCK_DATA).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"message": "Payload received!", "bytes": content_length}
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Starting Python API on port 8080...')
    httpd.serve_forever()
"@
Set-Content -Path "$AppDir\server.py" -Value $PythonCode
Write-Host "✅ Created Python API app ($AppDir\server.py)" -ForegroundColor Green


# 3. Create Dockerfile
$Dockerfile = @"
FROM python:3.9-slim
WORKDIR /app
COPY server.py .
EXPOSE 8080
CMD ["python", "server.py"]
"@
Set-Content -Path "$AppDir\Dockerfile" -Value $Dockerfile
Write-Host "✅ Created Dockerfile ($AppDir\Dockerfile)" -ForegroundColor Green


# 4. Create Kubernetes Deployment YAML
$DeploymentYaml = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-api-deployment
  labels:
    app: python-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: python-api
  template:
    metadata:
      labels:
        app: python-api
    spec:
      containers:
      - name: api-container
        image: python-api:v1
        imagePullPolicy: Never # Critical: Use local Minikube image
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "250m"
            memory: "256Mi"
        ports:
        - containerPort: 8080
"@
Set-Content -Path "$K8sDir\deployment.yaml" -Value $DeploymentYaml
Write-Host "✅ Created K8s Deployment ($K8sDir\deployment.yaml)" -ForegroundColor Green


# 5. Create Kubernetes Service YAML (LoadBalancer)
$ServiceYaml = @"
apiVersion: v1
kind: Service
metadata:
  name: python-api-service
spec:
  type: LoadBalancer
  selector:
    app: python-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
"@
Set-Content -Path "$K8sDir\service.yaml" -Value $ServiceYaml
Write-Host "✅ Created K8s Service ($K8sDir\service.yaml)" -ForegroundColor Green

Write-Host "`n🎉 Scaffolding Complete! To deploy:" -ForegroundColor Yellow
Write-Host "1. cd $LabName"
Write-Host "2. minikube docker-env | Invoke-Expression"
Write-Host "3. cd app && docker build -t python-api:v1 . && cd .."
Write-Host "4. kubectl apply -f k8s/"
