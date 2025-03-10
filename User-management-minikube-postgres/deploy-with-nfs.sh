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

# Set up NFS server if not already set up
if [ ! -f "nfs_setup_complete" ]; then
  echo "Setting up NFS server..."
  ./setup-nfs.sh
  touch nfs_setup_complete
  
  # Deploy NFS storage configurations
  echo "Deploying NFS storage configurations..."
  kubectl apply -f nfs-storage.yaml
fi

# Deploy PostgreSQL
echo "Deploying PostgreSQL with NFS storage..."
kubectl apply -f postgres-deployment.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL pod to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres --timeout=180s || true

# Deploy Flask application
echo "Deploying Flask application..."
kubectl apply -f flask-deployment.yaml

# Wait for Flask app to be ready
echo "Waiting for Flask pod to be ready..."
kubectl wait --for=condition=ready pod -l app=flask-thejas --timeout=60s || true

# Get the URL for the Flask service
echo "Getting the URL for the Flask service..."
minikube service flask-thejas --url

echo "Deployment complete! Access your Flask application at the URL above."