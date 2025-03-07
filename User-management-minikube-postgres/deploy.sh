#!/bin/bash

# Stop script on error
set -e

# Ensure Minikube is running
echo "Checking if Minikube is running..."
if ! minikube status | grep -q "Running"; then
  echo "Starting Minikube..."
  minikube start
fi

# Configure terminal to use Minikube's Docker daemon
echo "Configuring terminal to use Minikube's Docker daemon..."
eval $(minikube docker-env)

# Build the Docker image inside Minikube
echo "Building Docker image inside Minikube..."
docker build -t flask-thejas .

# Verify the image was created
echo "Verifying the image was created..."
docker images | grep flask-thejas

# Create directory structure in Minikube
echo "Creating the templates directory in Minikube..."
mkdir -p templates

# Deploy PostgreSQL StatefulSet to Minikube
echo "Deploying PostgreSQL StatefulSet to Minikube..."
kubectl apply -f postgres-statefulset.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL StatefulSet to be ready..."
kubectl wait --for=condition=ready pod postgres-0 --timeout=180s

# Deploy Flask application to Minikube
echo "Deploying Flask application to Minikube..."
kubectl apply -f flask-deployment.yaml

# Wait for the Flask pod to be ready
echo "Waiting for Flask pod to be ready..."
kubectl wait --for=condition=ready pod -l app=flask-thejas --timeout=60s

# Get the URL for the Flask service
echo "Getting the URL for the Flask service..."
minikube service flask-thejas --url

echo "Deployment complete! Access your Flask application at the URL above."