pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Pytest') {
            steps {
                sh '''
                    .venv/bin/python -m pytest -v \
                        --junitxml=results.xml \
                        --json-report \
                        --json-report-file=results.json
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'results.xml'
            archiveArtifacts allowEmptyArchive: true,
                artifacts: 'results.json'
        }
    }
}
