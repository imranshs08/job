# 🛡️ Jenkins to Azure Authentication Guide

## 1. The Why (Analogy)
Imagine Azure as a highly secure corporate building and Jenkins as a remote contractor trying to build out a new office (the AGC Lab) inside it. Without an ID badge, the contractor can't even get past the lobby. An **Azure Service Principal (SP)** is exactly this cryptographic ID badge. It grants Jenkins the *automated, headless ability* to swipe into your Azure Tenant, prove its identity, and execute deployment commands without needing a human to type in a username or password. 

## 2. Architecture
Jenkins authenticates to Azure via an **Azure Active Directory (Entra ID) App Registration**. 
This generates a Service Principal mapped to a specific role (e.g., `Contributor`) scoped tightly to a Resource Group or Subscription.

The architecture flows as follows:
1. Jenkins retrieves secure secrets (App ID, Tenant ID, Client Secret) from its internal native Credentials vault.
2. The Jenkins Pipeline executes an `az login --service-principal` command right before the `azure_agc_lab_manager.sh` script runs.
3. Azure replies with a short-lived bearer token, authorizing all subsequent `az aks create`, `az network`, and `az group` commands. 

---

## 3. Execution Commands (Implementation)

### Step 1: Create the Azure Service Principal
Run this from your local terminal (where you are already logged in to Azure):

```bash
# Set your target subscription
az account set --subscription "9d25952c-70d0-4818-9568-4f8c2b31d98f"

# Create the Service Principal scoped as Contributor to the specific Subscription (or tightly scoped to a Resource Group)
az ad sp create-for-rbac \
  --name "Jenkins-AGC-Deployer" \
  --role "Contributor" \
  --scopes /subscriptions/9d25952c-70d0-4818-9568-4f8c2b31d98f
```

**Keep the JSON output safe!** It looks like this:
```json
{
  "appId": "ab12345c-...",
  "displayName": "Jenkins-AGC-Deployer",
  "password": "super-secret-password-...",
  "tenant": "tenant-id-..."
}
```

### Step 2: Store Secrets in Jenkins
Navigate to **Jenkins Global Credentials** and create three **Secret text** credentials:
- **ID:** `AZURE_SP_APP_ID` (Value: `appId` from JSON)
- **ID:** `AZURE_SP_PASSWORD` (Value: `password` from JSON)
- **ID:** `AZURE_TENANT_ID` (Value: `tenant` from JSON)

### Step 3: Update the Jenkinsfile
We inject these credentials into the environment and add an `az login` step before our Bash script.

```diff
  environment {
      BREVO_API_KEY = credentials('brevo-api-key')
+     AZURE_APP_ID = credentials('AZURE_SP_APP_ID')
+     AZURE_PASSWORD = credentials('AZURE_SP_PASSWORD')
+     AZURE_TENANT_ID = credentials('AZURE_TENANT_ID')
  }

  stages {
      // Checkout stage...
      
      stage('Execute Lab Manager') {
          steps {
              script {
+                 echo "Authenticating with Azure CLI..."
+                 sh 'az login --service-principal -u $AZURE_APP_ID -p $AZURE_PASSWORD --tenant $AZURE_TENANT_ID'
+                 
                  echo "Executing azure_agc_lab_manager.sh with action: ${params.ACTION}"
                  sh 'chmod +x 16-Automation-Scripts/azure_agc_lab_manager.sh'
                  sh "bash 16-Automation-Scripts/azure_agc_lab_manager.sh ${params.ACTION}"
                  
+                 // Optional: Logout securely to clear token cache
+                 sh 'az logout'
              }
          }
      }
  }
```

---

## 4. Production Gotchas & Interview Traps

> [!WARNING]
> **Interview Trap:** "Why wouldn't you just use your personal Azure CLI login inside Jenkins?"
> **Answer:** Never use user-based identities (`az login --use-device-code` or personal accounts) in CI/CD pipelines. They lack lifecycle management, bypass auditing, and break immediately if the human employee leaves the company or changes their password. Always use headless Service Principals or workload identities.

> [!CAUTION]
> **Production Gotcha: The principle of Least Privilege**
> The `Contributor` role at the Subscription level is very permissive. In a true enterprise environment, SREs tightly constrain the scope (e.g., scoping the SP strictly to `/subscriptions/.../resourceGroups/rg-gateway-api-lab`). The script in question dynamically scales Subnets and Role Assignments to node RGs, which implies the SP needs a robust level of permissions, so test the scope meticulously during production rollout.

> [!TIP]
> **OIDC Federation / Workload Identity (Next-Gen SRE)** 
> If Jenkins is hosted on Kubernetes (like AKS), you can bypass Client Secrets entirely using OIDC (Workload Identity Federation). Jenkins authenticates dynamically via a Kubernetes Service Account instead of relying on passwords that can expire or leak. This is the gold standard for Azure authentication.

---

## 5. Complete Pipeline Reference (Jenkinsfile)

For absolute clarity, here is the complete, integrated `Jenkinsfile` that puts all of the concepts from above (checking out code, spinning up the resource via the Bash script, and reporting via Brevo Email API) into production.

```groovy
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
```
