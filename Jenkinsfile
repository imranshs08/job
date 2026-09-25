pipeline {
    agent any

    parameters {
        choice(name: 'ACTION', choices: ['status', 'up', 'down'], description: 'Manage Azure AGC Lab')
        string(name: 'NOTIFICATION_EMAIL', defaultValue: 'imranshs08@gmail.com', description: 'Email address to send the pipeline status')
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
                    bat "\"C:\\Program Files\\Git\\bin\\bash.exe\" -c \"chmod +x 16-Automation-Scripts/azure_agc_lab_manager.sh\""
                    bat "\"C:\\Program Files\\Git\\bin\\bash.exe\" 16-Automation-Scripts/azure_agc_lab_manager.sh ${params.ACTION}"
                }
            }
        }
    }

    post {
        always {
            script {
                if (params.NOTIFICATION_EMAIL) {
                    try {
                        def buildStatus = currentBuild.currentResult ?: "SUCCESS"
                        def subject = "Jenkins Job: ${env.JOB_NAME} Build ${env.BUILD_NUMBER} - ${buildStatus}"
                        def body = "Pipeline finished with status: ${buildStatus}. Please check Jenkins dashboard for detailed logs."
                        
                        def jsonPayload = """{"sender": {"name":"DevOps Jenkins", "email":"jenkins@domain.local"}, "to": [{"email": "${params.NOTIFICATION_EMAIL}"}], "subject": "${subject}", "htmlContent": "<p>${body}</p>"}"""

                        def response = powershell(
                            script: """
                            \$body = '${jsonPayload}'
                            try {
                                \$res = Invoke-RestMethod -Uri "https://api.brevo.com/v3/smtp/email" -Method Post -Headers @{ "accept" = "application/json"; "api-key" = \$env:BREVO_API_KEY; "content-type" = "application/json" } -Body \$body
                                Write-Output "Success"
                            } catch {
                                Write-Output "Brevo API Error: \$_"
                            }
                            """,
                            returnStdout: true
                        ).trim()
                        
                        echo "Brevo API HTTP context: ${response}"
                    } catch (Exception e) {
                        echo "Failed to send email notification! Ensure 'brevo-api-key' secret text credential is created in Jenkins. Error: ${e.message}"
                    }
                } else {
                    echo "NOTIFICATION_EMAIL parameter is empty; skipping email notification."
                }
            }
        }
    }
}
