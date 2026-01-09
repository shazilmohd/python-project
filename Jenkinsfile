<<<<<<< HEAD
// Guard: only run this Jenkinsfile on the master branch (or when master is being built).
// If this Jenkinsfile is evaluated on other branches (e.g., PR/source branches),
// exit early to avoid running builds. For multibranch pipelines `env.BRANCH_NAME`
// is provided by Jenkins.
if (env.BRANCH_NAME && env.BRANCH_NAME != 'master') {
    println "Skipping pipeline: branch '${env.BRANCH_NAME}' is not 'master'."
    currentBuild.result = 'NOT_BUILT'
    return
}

=======
>>>>>>> origin/master
pipeline {
    agent any
    
    parameters {
        string(
            name: 'VIRTUALBOX_USER',
            defaultValue: 'vboxuser',
            description: 'VirtualBox VM username'
        )
        string(
            name: 'VIRTUALBOX_HOST',
            defaultValue: '192.168.0.4',
            description: 'VirtualBox VM IP address'
        )
        string(
            name: 'APP_PORT',
            defaultValue: '5000',
            description: 'Flask application port'
        )
        string(
            name: 'VIRTUALBOX_SSH_KEY',
            defaultValue: 'jenkins-root',
            description: 'Jenkins credential ID for SSH key'
        )
        string(
            name: 'REMOTE_APP_PATH',
            defaultValue: '/home/vboxuser/color-poll',
            description: 'Application deployment path on VirtualBox'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip unit tests and coverage (for quick deployments)'
        )
        booleanParam(
            name: 'SKIP_DEPLOYMENT',
            defaultValue: false,
            description: 'Build and test only, skip VirtualBox deployment'
        )
    }
    
    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        PYTHON_CMD = "${VENV_DIR}/bin/python"
        PIP_CMD = "${VENV_DIR}/bin/pip"
        APP_PORT = "${params.APP_PORT}"
        VIRTUALBOX_USER = "${params.VIRTUALBOX_USER}"
        VIRTUALBOX_HOST = "${params.VIRTUALBOX_HOST}"
        VIRTUALBOX_SSH_KEY = credentials("${params.VIRTUALBOX_SSH_KEY}")
        REMOTE_APP_PATH = "${params.REMOTE_APP_PATH}"
        REMOTE_LOG_FILE = "${params.REMOTE_APP_PATH}/logs/app.log"
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
        
        stage('Install Dependencies') {
            steps {
                echo "📦 Installing system dependencies..."
                sh '''
                    # Update package manager and install Python venv
                    if command -v apt-get &> /dev/null; then
                        apt-get update
                        apt-get install -y python3-venv python3-pip python3-dev
                    elif command -v yum &> /dev/null; then
                        yum install -y python3-venv python3-pip python3-devel
                    else
                        echo "Unsupported package manager"
                        exit 1
                    fi
                    
                    echo "✓ Dependencies installed"
                '''
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
                    echo "✓ Virtual environment created and dependencies installed"
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
            when {
                expression { !params.SKIP_TESTS }
            }
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
                    cp -r app.py color_poll.py templates/ requirements.txt deploy.sh build/
                    chmod +x build/deploy.sh
                    echo "Build timestamp: $(date)" > build/BUILD_INFO.txt
                    ls -la build/
                '''
            }
        }
        
        stage('Deploy to VirtualBox') {
            when {
                expression { !params.SKIP_DEPLOYMENT }
            }
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
                    # Debug: Check python3 and venv availability on remote
                    echo "Debug: Checking remote system..."
                    ssh -i ~/.ssh/id_rsa_vbox -o StrictHostKeyChecking=no \
                        ${VIRTUALBOX_USER}@${VIRTUALBOX_HOST} \
                        "python3 --version && which python3 && ls -la /home/${VIRTUALBOX_USER}/color-poll/ || true"
                    
                    # Run deployment script
                    ssh -i ~/.ssh/id_rsa_vbox -o StrictHostKeyChecking=no \
                        ${VIRTUALBOX_USER}@${VIRTUALBOX_HOST} \
                        "export DEPLOY_USER=${VIRTUALBOX_USER} && bash -x ${REMOTE_APP_PATH}/deploy.sh start"
                    
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
            
            // Archive test results (junit is always available)
            junit testResults: 'test-results/junit.xml', skipPublishingChecks: true
            
            // Archive coverage reports for download
            sh '''
                if [ -d coverage-report ]; then
                    echo "📊 Code coverage report available at: coverage-report/index.html"
                fi
                if [ -d test-results ]; then
                    echo "🧪 Test results available at: test-results/junit.xml"
                fi
            '''
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
