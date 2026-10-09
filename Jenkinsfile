
pipeline {
    agent any

    environment {
        JIRA_URL = 'https://akashvelayutham2202.atlassian.net'
        JIRA_ISSUE = 'JAT-1'
    }

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
                script {
                    def exitCode = sh(
                        script: '''
                            .venv/bin/python -m pytest -v \
                                --junitxml=results.xml \
                                --json-report \
                                --json-report-file=results.json
                        ''',
                        returnStatus: true
                    )

                    env.PYTEST_EXIT_CODE = "${exitCode}"
                }
            }
        }

        stage('Publish Results to Jira') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'jira-email',
                        variable: 'JIRA_EMAIL'
                    ),
                    string(
                        credentialsId: 'jira-api-token',
                        variable: 'JIRA_API_TOKEN'
                    )
                ]) {
                    sh '''
                        .venv/bin/python scripts/publish_jira_results.py
                    '''
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true,
                  testResults: 'results.xml'

            archiveArtifacts allowEmptyArchive: true,
                  artifacts: 'results.json'
        }

        success {
            script {
                if (env.PYTEST_EXIT_CODE != '0') {
                    currentBuild.result = 'FAILURE'
                }
            }
        }
    }
}
