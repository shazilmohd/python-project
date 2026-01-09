# Jenkins CI/CD Configuration Guide

This guide explains how to configure Jenkins to run the Color Poll CI/CD pipeline with tests and coverage reports.

## Prerequisites

- Jenkins 2.300+ installed and running
- Git plugin installed
- Pipeline plugin installed
- HTML Publisher plugin installed (for coverage reports)

## Installation of Required Jenkins Plugins

1. **Go to Jenkins Dashboard** → **Manage Jenkins** → **Manage Plugins**
2. **Available Tab** → Search and install these plugins:
   - **Pipeline** (declarative pipeline support)
   - **Git** (Git integration)
   - **HTML Publisher** (for code coverage HTML reports)
   - **Email Extension Plugin** (optional, for notifications)
   - **Slack Notification Plugin** (optional, for Slack alerts)
   - **JUnit Plugin** (for test reporting)

3. Click **Install without restart** and restart Jenkins when done

## Step 1: Create SSH Credential for VirtualBox

1. Go to **Jenkins Dashboard** → **Manage Jenkins** → **Manage Credentials**
2. Click **Global** (or your preferred domain)
3. Click **Add Credentials** (top left)
4. Fill in the form:
   ```
   Kind: SSH Username with private key
   Scope: Global
   ID: jenkins-root  (must match VIRTUALBOX_SSH_KEY in Jenkinsfile)
   Description: VirtualBox VM SSH Key
   Username: vboxuser  (or your VirtualBox username)
   Private Key: (select "Enter directly" and paste your private key)
   ```
5. Click **Create**

### Generate SSH Key Pair (if you don't have one)

On your VirtualBox VM:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/jenkins_key
cat ~/.ssh/jenkins_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Copy the content of `~/.ssh/jenkins_key` and paste it into Jenkins credential.

## Step 2: Create Pipeline Job

1. **Jenkins Dashboard** → **New Item**
2. **Job Name**: `color-poll-pipeline`
3. **Type**: Select **Pipeline**
4. Click **OK**

## Step 3: Configure Pipeline Job

### General Settings
- **Description**: Color Poll Flask Application CI/CD Pipeline
- **GitHub project** (optional): `https://github.com/YOUR_USERNAME/color-poll`

### Build Triggers
Choose one or more:

**Option A: Poll SCM (check Git every 5 minutes)**
- Check **Poll SCM**
- Schedule: `H/5 * * * *` (polls every 5 minutes)

**Option B: GitHub Webhook (triggered on push)**
- Check **GitHub hook trigger for GITScm polling**
- Go to your GitHub repo → **Settings** → **Webhooks** → **Add webhook**
  - Payload URL: `http://your-jenkins-url/github-webhook/`
  - Content type: `application/json`
  - Trigger on: `Push events`

### Pipeline Configuration

1. **Definition**: Select **Pipeline script from SCM**
2. **SCM**: Git
3. **Repository URL**: 
   ```
   https://github.com/YOUR_USERNAME/color-poll.git
   ```
   OR
   ```
   git@github.com:YOUR_USERNAME/color-poll.git
   ```
4. **Credentials**: 
   - If using HTTPS: Add GitHub username/token credential
   - If using SSH: Add SSH key credential
5. **Branch Specifier**: `*/main` or `*/master`
6. **Script Path**: `Jenkinsfile` (default, don't change)

### Advanced Settings
- **Lightweight checkout**: Uncheck (to keep full history)
- Click **Save**

## Step 4: Configure VirtualBox SSH Details

Before running, **update the Jenkinsfile** with your VirtualBox configuration:

```groovy
environment {
    VIRTUALBOX_USER = "vboxuser"           // Your VM username
    VIRTUALBOX_HOST = "192.168.56.101"     // Your VM IP address
    VIRTUALBOX_SSH_KEY = credentials('jenkins-root')  // Jenkins credential ID
    REMOTE_APP_PATH = "/home/vboxuser/color-poll"
}
```

## Step 5: Configure VirtualBox VM for Deployment

On your VirtualBox VM:

```bash
# Create application directory
mkdir -p /home/vboxuser/color-poll/logs

# Install Python and pip
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Set up deploy.sh permissions
chmod +x /home/vboxuser/color-poll/deploy.sh
```

## Step 6: Run the Pipeline

1. **Jenkins Dashboard** → Select **color-poll-pipeline**
2. Click **Build Now** or wait for SCM polling/webhook trigger
3. Monitor the build:
   - **Console Output**: Shows real-time logs
   - **Test Results**: Click **Test Result** after build completes
   - **Code Coverage**: Click **Code Coverage Report** after build completes

## Expected Build Stages

```
✓ Checkout              - Clone repo from Git
✓ Setup Environment     - Create venv, install dependencies
✓ Lint & Code Quality   - Run flake8, syntax checks
✓ Unit Tests            - Run pytest with coverage
✓ Code Coverage Report  - Generate coverage report
✓ Build Artifacts       - Prepare files for deployment
✓ Deploy to VirtualBox  - Copy files via SCP
✓ Start Application     - SSH and run deploy.sh start
✓ Verify Deployment     - Health check via curl
```

## Post-Build Actions

### View Test Results
1. After build completes, click **Test Result**
2. View all test cases and pass/fail status

### View Code Coverage
1. After build completes, click **Code Coverage Report**
2. See line coverage, branch coverage, and uncovered lines
3. Click on file names to drill down

### Download Reports
- **JUnit XML**: `test-results/junit.xml`
- **Coverage XML**: `coverage-report/coverage.xml`
- **Coverage HTML**: `coverage-report/index.html`

## Troubleshooting

### SSH Connection Failed
```
Error: Permission denied (publickey)
```
**Solution**:
- Verify SSH key is added to VirtualBox VM: `cat ~/.ssh/authorized_keys`
- Check credential ID matches Jenkinsfile: `credentials('jenkins-root')`
- Test SSH manually: `ssh -i /var/lib/jenkins/.ssh/id_rsa vboxuser@192.168.56.101`

### Tests Failed
```
ModuleNotFoundError: No module named 'pytest'
```
**Solution**:
- `requirements.txt` should have pytest dependencies (already included)
- Check that Python venv is activated in build log

### Deployment Not Starting
```
bash: /home/vboxuser/color-poll/deploy.sh: No such file or directory
```
**Solution**:
- Ensure `deploy.sh` is in repository root
- Verify file permissions: `chmod +x deploy.sh`
- Check path in Jenkinsfile matches VirtualBox path

### Port Already in Use
```
Address already in use
```
**Solution**:
- Check if app is already running: `ps aux | grep "python3 app.py"`
- Stop it: `pkill -f "python3 app.py"`
- Deploy.sh should handle this automatically

## Optional: Email/Slack Notifications

### Email Notifications
Add to Jenkinsfile `post` section:
```groovy
failure {
    emailext(
        to: 'dev-team@example.com',
        subject: 'Build Failed: ${JOB_NAME}',
        body: 'Build ${BUILD_NUMBER} failed. Check console output at ${BUILD_URL}',
        attachmentsPattern: 'coverage-report/**/*'
    )
}
```

### Slack Notifications
Add to Jenkinsfile (requires Slack plugin):
```groovy
success {
    slackSend(
        channel: '#deployments',
        message: "✅ ${JOB_NAME} #${BUILD_NUMBER} deployed to VirtualBox"
    )
}
failure {
    slackSend(
        channel: '#deployments',
        color: 'danger',
        message: "❌ ${JOB_NAME} #${BUILD_NUMBER} deployment FAILED"
    )
}
```

---

## Summary

✅ Jenkins Pipeline with:
- Automated checkout from Git
- Python environment setup
- Code quality checks (flake8)
- Unit tests (pytest)
- Code coverage (pytest-cov)
- Automated deployment to VirtualBox
- Test and coverage report archiving

All configured with the provided Jenkinsfile!
