pipeline {
    agent any

    parameters {
        choice(name: 'ACTION', choices: ['status', 'up', 'down'], description: 'Manage Azure AGC Lab')
        string(name: 'NOTIFICATION_EMAIL', defaultValue: '', description: 'Email address to send the pipeline status')
    }

    environment {
        // Make sure to add a Secret Text credential with ID 'brevo-api-key' in Jenkins
        BREVO_API_KEY = credentials('brevo-api-key')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', credentialsId: 'github-credentials', url: 'https://github.com/imranshs08/job.git'
            }
        }

        stage('Execute Lab Manager') {
            steps {
                script {
                    echo "Executing azure_agc_lab_manager.sh with action: ${params.ACTION}"
                    sh 'chmod +x 16-Automation-Scripts/azure_agc_lab_manager.sh'
                    sh "bash 16-Automation-Scripts/azure_agc_lab_manager.sh ${params.ACTION}"
                }
            }
        }
    }

    post {
        always {
            script {
                if (params.NOTIFICATION_EMAIL) {
                    def buildStatus = currentBuild.currentResult ?: "SUCCESS"
                    def subject = "Jenkins Job: ${env.JOB_NAME} Build ${env.BUILD_NUMBER} - ${buildStatus}"
                    def body = "Pipeline finished with status: ${buildStatus}. Please check Jenkins dashboard for detailed logs."
                    
                    // Write payload to a file to safely handle JSON escaping
                    writeFile file: 'brevo_payload.json', text: """
                    {
                        "sender": {"name":"DevOps Jenkins", "email":"jenkins@domain.local"},
                        "to": [{"email": "${params.NOTIFICATION_EMAIL}"}],
                        "subject": "${subject}",
                        "htmlContent": "<p>${body}</p>"
                    }
                    """

                    // Use CURL to send email via Brevo REST API, escaping the GROOVY variables for the bash script properties
                    def response = sh(
                        script: '''
                        curl -s -w "\\n%{http_code}" -X POST 'https://api.brevo.com/v3/smtp/email' \\
                             -H 'accept: application/json' \\
                             -H "api-key: ${BREVO_API_KEY}" \\
                             -H 'content-type: application/json' \\
                             -d @brevo_payload.json
                        ''',
                        returnStdout: true
                    ).trim()
                    
                    echo "Brevo API HTTP context: ${response}"
                    sh 'rm -f brevo_payload.json'
                } else {
                    echo "NOTIFICATION_EMAIL parameter is empty; skipping email notification."
                }
            }
        }
    }
}
