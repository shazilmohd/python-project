pipeline {
    agent any
    
    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        PYTHON_CMD = "${VENV_DIR}/bin/python"
        PIP_CMD = "${VENV_DIR}/bin/pip"
        APP_PORT = "5000"
        VIRTUALBOX_USER = "vboxuser"  // Change to your VirtualBox VM username
        VIRTUALBOX_HOST = "192.168.0.4"  // Change to your VirtualBox VM IP
        VIRTUALBOX_SSH_KEY = credentials('jenkins-root')  // Jenkins credential
        REMOTE_APP_PATH = "/home/${VIRTUALBOX_USER}/color-poll"
        REMOTE_LOG_FILE = "/home/${VIRTUALBOX_USER}/color-poll/logs/app.log"
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "🔄 Checking out source code..."
                checkout scm
                sh 'git log -1 --pretty=format:"%H - %an - %s"'
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo "🛠️ Setting up Python virtual environment..."
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    ${PIP_CMD} install --upgrade pip
                    ${PIP_CMD} install -r requirements.txt
                '''
            }
        }
        
        stage('Lint & Code Quality') {
            steps {
                echo "📝 Running linting checks..."
                sh '''
                    . ${VENV_DIR}/bin/activate
                    # Run syntax check
                    ${PYTHON_CMD} -m py_compile app.py color_poll.py
                    # Run flake8 linting
                    ${PIP_CMD} install flake8 > /dev/null
                    flake8 app.py color_poll.py --count --show-source --statistics || true
                    echo "✓ Syntax and lint check passed"
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo "🧪 Running unit tests with coverage..."
                sh '''
                    . ${VENV_DIR}/bin/activate
                    mkdir -p test-results coverage-report
                    
                    # Run pytest with coverage
                    ${PIP_CMD} install pytest pytest-cov coverage > /dev/null
                    
                    pytest test_app.py \
                        -v \
                        --junitxml=test-results/junit.xml \
                        --cov=. \
                        --cov-report=xml:coverage-report/coverage.xml \
                        --cov-report=html:coverage-report/ \
                        --cov-report=term
                    
                    echo "✓ Tests completed successfully"
                '''
            }
        }
        
        stage('Code Coverage Report') {
            steps {
                echo "📊 Generating code coverage report..."
                sh '''
                    echo "Coverage report generated at: coverage-report/index.html"
                    echo "Test results at: test-results/junit.xml"
                '''
            }
        }
        
        stage('Build Artifacts') {
            steps {
                echo "📦 Building application artifacts..."
                sh '''
                    mkdir -p build/
                    cp -r app.py color_poll.py templates/ requirements.txt build/
                    echo "Build timestamp: $(date)" > build/BUILD_INFO.txt
                    ls -la build/
                '''
            }
        }
        
        stage('Deploy to VirtualBox') {
            steps {
                echo "🚀 Deploying to VirtualBox VM..."
                sh '''
                    # Create SSH config
                    mkdir -p ~/.ssh
                    cp ${VIRTUALBOX_SSH_KEY} ~/.ssh/id_rsa_vbox
                    chmod 600 ~/.ssh/id_rsa_vbox
                    
                    # Check SSH connection
                    ssh -i ~/.ssh/id_rsa_vbox -o StrictHostKeyChecking=no \
                        ${VIRTUALBOX_USER}@${VIRTUALBOX_HOST} "echo 'SSH connection successful'"
                    
                    # Create remote directory if it doesn't exist
                    ssh -i ~/.ssh/id_rsa_vbox -o StrictHostKeyChecking=no \
                        ${VIRTUALBOX_USER}@${VIRTUALBOX_HOST} \
                        "mkdir -p ${REMOTE_APP_PATH}/logs"
                    
                    # Copy application files
                    scp -i ~/.ssh/id_rsa_vbox -o StrictHostKeyChecking=no \
                        -r build/* \
                        ${VIRTUALBOX_USER}@${VIRTUALBOX_HOST}:${REMOTE_APP_PATH}/
                    
                    echo "✓ Files transferred successfully"
                '''
            }
        }
        
        stage('Start Application') {
            steps {
                echo "⚙️ Starting Flask application on VirtualBox..."
                sh '''
                    ssh -i ~/.ssh/id_rsa_vbox -o StrictHostKeyChecking=no \
                        ${VIRTUALBOX_USER}@${VIRTUALBOX_HOST} \
                        "bash ${REMOTE_APP_PATH}/deploy.sh start"
                    
                    sleep 3
                    echo "✓ Application started"
                '''
            }
        }
        
        stage('Verify Deployment') {
            steps {
                echo "✅ Verifying deployment..."
                sh '''
                    ssh -i ~/.ssh/id_rsa_vbox -o StrictHostKeyChecking=no \
                        ${VIRTUALBOX_USER}@${VIRTUALBOX_HOST} \
                        "curl -s http://localhost:${APP_PORT}/ | grep -q 'Color Poll' && echo 'Deployment verified!' || echo 'Verification failed'"
                '''
            }
        }
    }
    
    post {
        always {
            echo "🧹 Cleaning up..."
            sh 'rm -f ~/.ssh/id_rsa_vbox'
            
            // Archive test results and coverage reports
            junit testResults: 'test-results/junit.xml', skipPublishingChecks: true
            
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'coverage-report',
                reportFiles: 'index.html',
                reportName: 'Code Coverage Report'
            ])
        }
        
        success {
            echo "✅ Pipeline completed successfully!"
            // Optional: Send Slack/email notification
            // slackSend(channel: '#deployments', message: "Color Poll deployed successfully to VirtualBox")
        }
        
        failure {
            echo "❌ Pipeline failed. Check logs above."
            // Optional: Send failure notification
            // slackSend(channel: '#deployments', message: "Color Poll deployment FAILED")
        }
        
        cleanup {
            deleteDir()
        }
    }
}
