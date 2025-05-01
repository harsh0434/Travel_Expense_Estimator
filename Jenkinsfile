pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        VENV_PATH = 'venv'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python') {
            steps {
                sh """
                    python -m venv ${VENV_PATH}
                    . ${VENV_PATH}/bin/activate
                    pip install -r requirements.txt
                """
            }
        }
        
        stage('Run Tests') {
            steps {
                sh """
                    . ${VENV_PATH}/bin/activate
                    pytest tests/ --cov=. --cov-report=html
                """
            }
        }
        
        stage('Build Docker') {
            steps {
                script {
                    docker.build('travel-calculator:latest')
                }
            }
        }
        
        stage('Deploy to Render') {
            when {
                branch 'main'
            }
            steps {
                sh """
                    curl -X POST https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys \
                    -H "Authorization: Bearer $RENDER_API_KEY"
                """
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            emailext body: 'Build successful!', subject: 'Build Success', to: '${EMAIL_RECIPIENTS}'
        }
        failure {
            emailext body: 'Build failed!', subject: 'Build Failure', to: '${EMAIL_RECIPIENTS}'
        }
    }
} 