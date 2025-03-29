#!/bin/bash

# Exit on error
set -e

# Install Java
echo "Installing Java..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install openjdk@11
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y openjdk-11-jdk
else
    echo "Please install Java 11 manually"
    exit 1
fi

# Install Jenkins and dependencies
echo "Installing Jenkins and dependencies..."
sudo apt-get update
sudo apt-get install -y openjdk-11-jdk
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install -y jenkins

# Install Docker
echo "Installing Docker..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install --cask docker
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
else
    echo "Please install Docker manually"
    exit 1
fi

# Start Jenkins service
echo "Starting Jenkins service..."
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Wait for Jenkins to start
echo "Waiting for Jenkins to start..."
sleep 30

# Get initial admin password
echo "Getting initial admin password..."
ADMIN_PASSWORD=$(sudo cat /var/lib/jenkins/secrets/initialAdminPassword)
echo "Initial admin password: $ADMIN_PASSWORD"

# Install Jenkins CLI
echo "Installing Jenkins CLI..."
wget http://localhost:8080/jnlpJars/jenkins-cli.jar

# Install required plugins
echo "Installing required plugins..."
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth admin:$ADMIN_PASSWORD install-plugin \
    workflow-aggregator \
    git \
    github \
    docker-workflow \
    blueocean \
    pipeline-stage-view \
    junit \
    cobertura

# Create Jenkins pipeline job
echo "Creating Jenkins pipeline job..."
cat > job.xml << EOL
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>Travel Expense Estimator CI/CD Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition">
    <scm class="hudson.plugins.git.GitSCM">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>\${GITHUB_REPO_URL}</url>
          <credentialsId>github-credentials</credentialsId>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
  </definition>
  <triggers>
    <hudson.triggers.SCMTrigger>
      <spec>H/5 * * * *</spec>
    </hudson.triggers.SCMTrigger>
  </triggers>
</flow-definition>
EOL

# Create Jenkinsfile
echo "Creating Jenkinsfile..."
cat > Jenkinsfile << EOL
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'travel-app'
        DOCKER_TAG = "\${BUILD_NUMBER}"
        PYTHON_VERSION = '3.9'
    }
    
    stages {
        stage('Setup Python') {
            steps {
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest --cov=. --cov-report=xml
                '''
            }
            post {
                always {
                    junit 'test-results/*.xml'
                    cobertura coberturaReportFile: 'coverage.xml'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("\${DOCKER_IMAGE}:\${DOCKER_TAG}")
                }
            }
        }
        
        stage('Deploy to Staging') {
            when { branch 'main' }
            steps {
                script {
                    docker.withRegistry('https://registry.example.com', 'registry-credentials') {
                        docker.image("\${DOCKER_IMAGE}:\${DOCKER_TAG}").push('staging')
                    }
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    docker.withRegistry('https://registry.example.com', 'registry-credentials') {
                        docker.image("\${DOCKER_IMAGE}:\${DOCKER_TAG}").push('latest')
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            emailext (
                subject: "Pipeline Success: \${currentBuild.fullDisplayName}",
                body: "The pipeline completed successfully.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
        failure {
            emailext (
                subject: "Pipeline Failed: \${currentBuild.fullDisplayName}",
                body: "The pipeline failed. Please check the logs.",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
    }
}
EOL

# Create credentials for GitHub and Docker registry
echo "Please set up the following credentials in Jenkins:"
echo "1. GitHub credentials (ID: github-credentials)"
echo "2. Docker registry credentials (ID: registry-credentials)"

echo "Jenkins setup completed successfully!"
echo "Please visit http://localhost:8080 and complete the following steps:"
echo "1. Log in with the initial admin password shown above"
echo "2. Install suggested plugins"
echo "3. Create an admin user"
echo "4. Configure GitHub and Docker registry credentials"
echo "5. Create a new pipeline job using the job.xml file" 