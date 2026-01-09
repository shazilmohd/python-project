#!/bin/bash

# Color Poll Deployment Script for VirtualBox
# Usage: ./deploy.sh {start|stop|restart|status}

set -e

# Get current user (use environment variable if set, otherwise current user)
CURRENT_USER="${DEPLOY_USER:=$(whoami)}"
APP_DIR="/home/${CURRENT_USER}/color-poll"
VENV_DIR="${APP_DIR}/venv"
LOG_DIR="${APP_DIR}/logs"
LOG_FILE="${LOG_DIR}/app.log"
PID_FILE="${APP_DIR}/.app.pid"
PORT=5000

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOG_FILE}"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "${LOG_FILE}"
}

setup_environment() {
    log_info "Setting up Python environment..."
    
    if [ ! -d "${VENV_DIR}" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv "${VENV_DIR}"
    fi
    
    # Activate venv and install dependencies
    source "${VENV_DIR}/bin/activate"
    
    if [ -f "${APP_DIR}/requirements.txt" ]; then
        log_info "Installing dependencies..."
        pip install --quiet --upgrade pip
        pip install --quiet -r "${APP_DIR}/requirements.txt"
    fi
    
    deactivate
    log_info "Environment setup complete"
}

start_app() {
    log_info "Starting Flask application on port ${PORT}..."
    
    if [ -f "${PID_FILE}" ]; then
        OLD_PID=$(cat "${PID_FILE}")
        if kill -0 "${OLD_PID}" 2>/dev/null; then
            log_warn "Application already running with PID ${OLD_PID}"
            return
        else
            rm -f "${PID_FILE}"
        fi
    fi
    
    setup_environment
    
    # Start the Flask app in the background
    source "${VENV_DIR}/bin/activate"
    cd "${APP_DIR}"
    
    nohup python app.py >> "${LOG_FILE}" 2>&1 &
    NEW_PID=$!
    echo "${NEW_PID}" > "${PID_FILE}"
    
    deactivate
    
    sleep 2
    
    if kill -0 "${NEW_PID}" 2>/dev/null; then
        log_info "✓ Application started successfully (PID: ${NEW_PID})"
    else
        log_error "Failed to start application"
        return 1
    fi
}

stop_app() {
    log_info "Stopping Flask application..."
    
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat "${PID_FILE}")
        if kill -0 "${PID}" 2>/dev/null; then
            kill "${PID}" || true
            sleep 1
            if kill -0 "${PID}" 2>/dev/null; then
                kill -9 "${PID}" || true
            fi
            log_info "✓ Application stopped (PID: ${PID})"
        else
            log_warn "PID file exists but process not running"
        fi
        rm -f "${PID_FILE}"
    else
        log_warn "No PID file found. Application may not be running."
    fi
}

restart_app() {
    log_info "Restarting Flask application..."
    stop_app
    sleep 1
    start_app
}

status_app() {
    if [ -f "${PID_FILE}" ]; then
        PID=$(cat "${PID_FILE}")
        if kill -0 "${PID}" 2>/dev/null; then
            log_info "✓ Application is running (PID: ${PID})"
            netstat -tlnp 2>/dev/null | grep "${PORT}" || true
            return 0
        else
            log_error "PID file exists but process not running"
            return 1
        fi
    else
        log_error "✗ Application is not running"
        return 1
    fi
}

show_logs() {
    log_info "Last 50 lines of application log:"
    tail -50 "${LOG_FILE}"
}

# Main script logic
case "${1:-status}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        status_app
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac

exit 0
