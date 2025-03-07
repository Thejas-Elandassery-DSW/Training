#!/bin/bash

# Delete the Flask deployment and service
echo "Deleting Flask deployment and service..."
kubectl delete -f flask-deployment.yaml

# Delete the PostgreSQL deployment and service
echo "Deleting PostgreSQL Statefulset and service..."
kubectl delete -f postgres-statefulset.yaml

echo "Cleanup complete!"