#!/bin/bash

# Application maintenance script with various options

# Function to display usage information
function display_help {
    echo "Usage: $0 [option]"
    echo "Options:"
    echo "  update           - Rebuild and update the application"
    echo "  restart          - Restart the application without rebuilding"
    echo "  logs             - Show logs from the Flask application"
    echo "  status           - Show status of all deployments and pods"
    echo "  describe         - Describe the Flask deployment (for troubleshooting)"
    echo "  port-forward     - Set up port forwarding to access the app directly"
    echo "  db-shell         - Open a PostgreSQL shell inside the database pod"
    echo "  watch-templates  - Watch template directory and auto-update on changes"
    echo "  help             - Display this help message"
    echo
    echo "Example: $0 update"
}

# Setup environment for Minikube
function setup_env {
    eval $(minikube docker-env)
}

# Function to update the application
function update_app {
    setup_env
    echo "🏗️ Rebuilding and updating application..."
    docker build -t flask-thejas .
    kubectl rollout restart deployment flask-thejas
    kubectl rollout status deployment/flask-thejas
    minikube service flask-thejas --url
}

# Function to restart the application
function restart_app {
    echo "🔄 Restarting application..."
    kubectl rollout restart deployment flask-thejas
    kubectl rollout status deployment/flask-thejas
}

# Function to show logs
function show_logs {
    echo "📜 Showing logs from Flask application..."
    POD_NAME=$(kubectl get pods -l app=flask-thejas -o jsonpath="{.items[0].metadata.name}")
    kubectl logs -f $POD_NAME
}

# Function to show status
function show_status {
    echo "📊 Kubernetes resources status:"
    echo "=== Deployments ==="
    kubectl get deployments
    echo
    echo "=== Pods ==="
    kubectl get pods
    echo
    echo "=== Services ==="
    kubectl get services
}

# Function to describe the deployment
function describe_deployment {
    echo "🔍 Describing Flask deployment..."
    kubectl describe deployment flask-thejas
    
    echo
    echo "🔍 Describing Flask pod..."
    POD_NAME=$(kubectl get pods -l app=flask-thejas -o jsonpath="{.items[0].metadata.name}")
    kubectl describe pod $POD_NAME
}

# Function to setup port forwarding
function port_forward {
    POD_NAME=$(kubectl get pods -l app=flask-thejas -o jsonpath="{.items[0].metadata.name}")
    echo "🔌 Setting up port forwarding for pod $POD_NAME..."
    echo "⚠️  Press Ctrl+C to stop port forwarding"
    kubectl port-forward $POD_NAME 5000:5000
}

# Function to open a database shell
function db_shell {
    DB_POD_NAME=$(kubectl get pods -l app=postgres -o jsonpath="{.items[0].metadata.name}")
    echo "🗄️  Opening PostgreSQL shell in pod $DB_POD_NAME..."
    kubectl exec -it $DB_POD_NAME -- psql -U postgres -d userdb
}

# Function to watch templates
function watch_templates {
    echo "👀 Watching templates directory for changes..."
    echo "Press Ctrl+C to stop watching"
    
    touch .last_update
    
    while true; do
        if find templates -type f -newer .last_update | grep -q .; then
            echo "🔍 Detected changes in templates directory!"
            touch .last_update
            update_app
            echo "💤 Continuing to watch for changes..."
        fi
        sleep 2
    done
}

# Main script logic
if [ $# -eq 0 ]; then
    display_help
    exit 1
fi

case "$1" in
    update)
        update_app
        ;;
    restart)
        restart_app
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    describe)
        describe_deployment
        ;;
    port-forward)
        port_forward
        ;;
    db-shell)
        db_shell
        ;;
    watch-templates)
        watch_templates
        ;;
    help)
        display_help
        ;;
    *)
        echo "❌ Unknown option: $1"
        display_help
        exit 1
        ;;
esac

exit 0