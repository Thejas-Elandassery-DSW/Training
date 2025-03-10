#!/bin/bash

# Stop script on error
set -e

echo "Setting up NFS provisioner in Minikube..."

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
  echo "Starting Minikube..."
  minikube start
fi

# Create NFS directory in Minikube node
echo "Creating NFS directory in Minikube..."
minikube ssh "sudo mkdir -p /data/nfs && sudo chmod -R 777 /data/nfs"

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

# Create a simple NFS server configuration
cat <<EOF > nfs-server.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nfs-server
spec:
  selector:
    matchLabels:
      app: nfs-server
  template:
    metadata:
      labels:
        app: nfs-server
    spec:
      containers:
      - name: nfs-server
        image: itsthenetwork/nfs-server-alpine:latest
        securityContext:
          privileged: true
        env:
        - name: SHARED_DIRECTORY
          value: /data
        volumeMounts:
        - mountPath: /data
          name: nfs-vol
      volumes:
      - name: nfs-vol
        hostPath:
          path: /data/nfs
---
apiVersion: v1
kind: Service
metadata:
  name: nfs-server
spec:
  ports:
  - name: nfs
    port: 2049
    protocol: TCP
    targetPort: 2049
  - name: mountd
    port: 20048
    protocol: TCP
    targetPort: 20048
  - name: rpcbind
    port: 111
    protocol: TCP
    targetPort: 111
  selector:
    app: nfs-server
EOF

# Apply the NFS server configuration
echo "Deploying NFS server..."
kubectl apply -f nfs-server.yaml

# Wait for NFS server to be ready
echo "Waiting for NFS server to be ready..."
kubectl wait --for=condition=ready pod -l app=nfs-server --timeout=120s

# Get NFS server Pod IP
NFS_SERVER_IP=$(kubectl get pod -l app=nfs-server -o jsonpath='{.items[0].status.podIP}')
echo "NFS Server Pod IP: $NFS_SERVER_IP"

# Create storage class, PV and PVC
cat <<EOF > nfs-storage.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: Immediate
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs-storage
  nfs:
    server: $NFS_SERVER_IP
    path: /data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: nfs-storage
  resources:
    requests:
      storage: 1Gi
EOF

echo "NFS server set up complete!"
echo "Created NFS storage configuration in nfs-storage.yaml"

echo "Next steps:"
echo "1. Deploy the storage configuration: kubectl apply -f nfs-storage.yaml"
echo "2. Deploy PostgreSQL with NFS: kubectl apply -f postgres-deployment.yaml"
echo "3. Deploy your Flask application: kubectl apply -f flask-deployment.yaml"