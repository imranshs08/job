pipeline {
    agent any

    options {
        timestamps()
    }

    parameters {
        choice(name: 'ACTION', choices: ['status', 'up', 'down'], description: 'Manage Azure AGC Lab')
        string(name: 'NOTIFICATION_EMAIL', defaultValue: 'imranshs08@gmail.com', description: 'Email address to send the pipeline status')
    }

    environment {
        // Make sure to add a Secret Text credential with ID 'brevo-api-key' in Jenkins
        BREVO_API_KEY = credentials('brevo-api-key')
        AZURE_SP_APP_ID = credentials('AZURE_SP_APP_ID')
        AZURE_SP_PASSWORD = credentials('AZURE_SP_PASSWORD')
        AZURE_TENANT_ID = credentials('AZURE_TENANT_ID')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', credentialsId: 'github-credentials', url: 'https://github.com/imranshs08/job.git'
            }
        }

        stage('Azure Authentication') {
            steps {
                script {
                    echo "Logging into Azure seamlessly with Service Principal..."
                    bat "az login --service-principal -u %AZURE_SP_APP_ID% -p %AZURE_SP_PASSWORD% --tenant %AZURE_TENANT_ID%"
                }
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
                        def actionColor = params.ACTION == 'up' ? '#e0f2f1' : (params.ACTION == 'down' ? '#ffebee' : '#fff3e0')
                        def actionTextColor = params.ACTION == 'up' ? '#00796b' : (params.ACTION == 'down' ? '#c62828' : '#e65100')
                        def statusColor = buildStatus == 'SUCCESS' ? '#e8f5e9' : '#ffebee'
                        def statusTextColor = buildStatus == 'SUCCESS' ? '#2e7d32' : '#c62828'
                        
                        def body = """
                        <div style='font-family: \"Segoe UI\", Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: auto; background-color: #f8f9fa; padding: 30px; border-radius: 12px; border: 1px solid #eaebec; box-shadow: 0 4px 15px rgba(0,0,0,0.05);'>
                            <h2 style='color: #2b3a42; text-align: center; margin-bottom: 5px; font-weight: 600;'>🚀 Automation Report</h2>
                            <p style='text-align: center; color: #7f8c8d; font-size: 14px; margin-top: 0;'>Azure AGC Infrastructure Manager</p>
                            <hr style='border: none; border-top: 1px solid #eaebec; margin: 25px 0;'>
                            
                            <table style='width: 100%; border-collapse: collapse; font-size: 15px;'>
                                <tr>
                                    <td style='padding: 12px; font-weight: bold; color: #555; width: 40%;'>Pipeline Name:</td>
                                    <td style='padding: 12px; color: #222;'>${env.JOB_NAME}</td>
                                </tr>
                                <tr style='background-color: #ffffff;'>
                                    <td style='padding: 12px; font-weight: bold; color: #555;'>Build Trigger:</td>
                                    <td style='padding: 12px; color: #222;'>#${env.BUILD_NUMBER}</td>
                                </tr>
                                <tr>
                                    <td style='padding: 12px; font-weight: bold; color: #555;'>Action Executed:</td>
                                    <td style='padding: 12px; color: #222;'><span style='background: ${actionColor}; color: ${actionTextColor}; padding: 4px 10px; border-radius: 6px; font-weight: bold; text-transform: uppercase;'>${params.ACTION}</span></td>
                                </tr>
                                <tr style='background-color: #ffffff;'>
                                    <td style='padding: 12px; font-weight: bold; color: #555;'>Final Status:</td>
                                    <td style='padding: 12px;'>
                                        <span style='background: ${statusColor}; color: ${statusTextColor}; padding: 6px 14px; border-radius: 6px; font-weight: bold;'>
                                            ${buildStatus}
                                        </span>
                                    </td>
                                </tr>
                            </table>
                            
                            <div style='text-align: center; margin-top: 35px;'>
                                <a href='${env.BUILD_URL}console' style='background-color: #0078d4; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 15px; display: inline-block; box-shadow: 0 2px 5px rgba(0,120,212,0.3);'>View Console Log</a>
                            </div>
                            <p style='text-align: center; color: #a5b1c2; font-size: 12px; margin-top: 35px;'>Generated by Jenkins • DevOps Job Switch 2027</p>
                        </div>
                        """
                        
                        def cleanBody = body.replaceAll("\n", "").replaceAll("  ", "").replace('"', '\\"')
                        
                        def jsonPayload = """{"sender": {"name":"DevOps Jenkins", "email":"imranshs08@12050952.brevosend.com"}, "to": [{"email": "${params.NOTIFICATION_EMAIL}"}], "subject": "${subject}", "htmlContent": "${cleanBody}"}"""


                        def response = powershell(
                            script: """
\$body = @'
${jsonPayload}
'@
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
