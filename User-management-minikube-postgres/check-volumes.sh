#!/bin/bash

# Display PersistentVolumeClaims
echo "=== PersistentVolumeClaims ==="
kubectl get pvc

# Display PersistentVolumes
echo -e "\n=== PersistentVolumes ==="
kubectl get pv

# Display detailed info about the PostgreSQL StatefulSet
echo -e "\n=== PostgreSQL StatefulSet Details ==="
kubectl describe statefulset postgres

# Check the capacity of the PVC
echo -e "\n=== Storage Capacity ==="
POSTGRES_PVC=$(kubectl get pvc -l app=postgres -o jsonpath='{.items[0].metadata.name}')
if [ -n "$POSTGRES_PVC" ]; then
  kubectl get pvc $POSTGRES_PVC -o jsonpath='{.spec.resources.requests.storage}'
  echo
else
  echo "PostgreSQL PVC not found. Make sure the StatefulSet is deployed."
fi