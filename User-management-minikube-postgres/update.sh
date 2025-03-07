#!/bin/bash

# Stop script on error
set -e

echo "🔄 Starting application update process..."

# Configure terminal to use Minikube's Docker daemon
echo "🐳 Configuring terminal to use Minikube's Docker daemon..."
eval $(minikube docker-env)

# Rebuild the Docker image inside Minikube
echo "🏗️ Rebuilding Docker image inside Minikube..."
docker build -t flask-thejas .

# Verify the image was recreated
echo "✅ Verifying the updated image was created..."
docker images | grep flask-thejas

# Restart the Flask pods to pick up the new image
echo "🔄 Restarting Flask pods to use the updated image..."
kubectl rollout restart deployment flask-thejas

# Wait for the new pods to be ready
echo "⏳ Waiting for updated pods to be ready..."
kubectl rollout status deployment/flask-thejas --timeout=60s

# Get the URL for the Flask service
echo "🌐 Getting the URL for the Flask service..."
FLASK_URL=$(minikube service flask-thejas --url)

echo "✨ Update complete! Access your updated Flask application at: $FLASK_URL"

# Optionally open the application in the default browser
if command -v xdg-open &> /dev/null; then
    echo "🌐 Opening application in browser..."
    xdg-open $FLASK_URL
elif command -v open &> /dev/null; then
    echo "🌐 Opening application in browser..."
    open $FLASK_URL
else
    echo "📝 Please open this URL in your browser: $FLASK_URL"
fi

# Show pod status
echo "📊 Current pod status:"
kubectl get pods | grep flask-thejas