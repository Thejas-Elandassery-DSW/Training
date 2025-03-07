# Flask User Data Management with Kubernetes

This project is a simple Flask application that allows users to post and view user data. The application is containerized using Docker and deployed on Minikube.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Project Structure

```
project/
├── app.py                     # Flask application
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── home.html             # Home page
│   ├── post_data.html        # Form for posting data
│   └── see_data.html         # Page for viewing data
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── postgres-deployment.yaml   # Kubernetes manifest for PostgreSQL
├── flask-deployment.yaml      # Kubernetes manifest for Flask
├── deploy.sh                  # Deployment script
└── README.md                  # Documentation
```

## Getting Started

1. Ensure Minikube is installed and running:

```bash
minikube start
```

2. Make the deployment script executable:

```bash
chmod +x deploy.sh
```

3. Run the deployment script:

```bash
./deploy.sh
```

4. The script will:
   - Configure your terminal to use Minikube's Docker daemon
   - Build the Docker image inside Minikube
   - Deploy PostgreSQL and the Flask application to Minikube
   - Display the URL to access the application

5. Access the application using the provided URL

## Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

1. Configure terminal to use Minikube's Docker daemon:

```bash
eval $(minikube docker-env)
```

2. Build the Docker image inside Minikube:

```bash
docker build -t flask-thejas .
```

3. Deploy PostgreSQL:

```bash
kubectl apply -f postgres-deployment.yaml
```

4. Deploy the Flask application:

```bash
kubectl apply -f flask-deployment.yaml
```

5. Get the service URL:

```bash
minikube service flask-thejas --url
```

## Application Usage

1. Access the application using the provided URL
2. On the home page, choose either "Post Data" or "See Data"
3. To add a new user, click "Post Data", fill the form, and submit
4. To view all users, click "See Data"

## Troubleshooting

If the pods are not running properly, you can check their status:

```bash
kubectl get pods
```

To view logs for a specific pod:

```bash
kubectl logs <pod-name>
```

To delete and recreate a deployment:

```bash
kubectl delete -f flask-deployment.yaml
kubectl apply -f flask-deployment.yaml
```