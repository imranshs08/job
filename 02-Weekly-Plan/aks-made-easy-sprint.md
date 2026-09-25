# 🚀 Azure Kubernetes Services (AKS) Made Easy - 20 Day Sprint

> **Target:** Master AKS End-to-End before $200 Azure Credit Expires.
> **Total Lectures:** 183
> **Timeline:** Sep 22, 2026 to Oct 11, 2026
> **Primary Source:** [Kalyan Reddy Daida (Udemy)](https://www.udemy.com/course/azure-kubernetes-services-aks-made-easy/)

This specialized 20-day sprint suspends all other non-Kubernetes study plans. The primary focus is deeply mastering Azure-native Kubernetes deployments, operations, and security.

## Day 1: Intro to AKS & Containers (Sep 22, 2026)
- [x] **Objective:** What is K8s, Docker basics, AKS architecture.
- [x] **Lectures:** Watch #1–10 (`⏱️ 47m Total`)
    * **[7min]** 1. Introduction about instructor and course
    * **[3min]** 2. Good to have / Recommended background
    * **[0min]** 3. Connect with me
    * **[9min]** 4. [What is a container and how is it different from a VM?](../../04-Notes/04-Kubernetes/AKS-Masterclass/02_Container_Isolation_Namespaces_and_Cgroups.md)
    * **[2min]** 5. [Microservices architecture](../../04-Notes/04-Kubernetes/AKS-Masterclass/03_Microservices_Architecture.md)
    * **[7min]** 6. [What are Docker, Dockerfile and Docker Hub?](../../04-Notes/04-Kubernetes/AKS-Masterclass/04_Docker_Dockerfile_DockerHub.md)
    * **[7min]** 7. [Creating our first container app (web app), pushing it to Docker Hub and running](../../04-Notes/04-Kubernetes/AKS-Masterclass/05_Container_Web_App_Build_and_Push.md)
    * **[7min]** 8. Create our 2nd container app (troubleshooting app), push it to DHub and run it
    * **[2min]** 9. Understanding why we need a container orchestrator, like Kubernetes
    * **[3min]** 10. Introduction to Kubernetes

- [x] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 2: Cluster Provisioning (Sep 23, 2026)
- [x] **Objective:** Cluster types, control plane access, public vs private, VNET integration.
- [x] **Lectures:** Watch #11–20 (`⏱️ 1h 16m Total`)
    * **[12min]** 11. Kubernetes architecture
    * **[6min]** 12. Self-managed vs Cloud-managed Kubernetes cluster
    * **[5min]** 13. What is Azure Kubernetes Service (AKS)?
    * **[6min]** 14. Azure pricing, free account and AKS cost
    * **[14min]** 15. Considerations for saving cost on AKS
    * **[2min]** 16. Login to Azure and set the subscription
    * **[11min]** 17. Let's create our first AKS cluster
    * **[8min]** 18. Install CLI, explore Azure Cloud Shell, connect to the cluster
    * **[3min]** 19. aks-preview extension and feature registration
    * **[9min]** 20. Making our life easier with autocompletion, alias, Kubernetes and AKS extension

- [x] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 3: Node Pools Mastery (Sep 24, 2026)
- [x] **Objective:** System vs User node pools, scaling nodes, Spot instances.
- [x] **Lectures:** Watch #21–30 (`⏱️ 54m Total`)
    * **[7min]** 21. PowerShell Basics in AKS - Connect to Azure, AKS creation, completion, aliases
    * **[5min]** 22. Imperative and declarative approaches
    * **[17min]** 23. Practice with Nodes, Pod, Deployment, Replicaset, DaemonSet, Service, Secret, CM
    * **[6min]** 24. Understanding our CIDRs
    * **[3min]** 25. What is a node pool?
    * **[4min]** 26. Connect to AKS nodes - quick demo
    * **[3min]** 27. Exploring the AKS cluster - Kubernetes side
    * **[3min]** 28. kubelet
    * **[4min]** 29. containerd
    * **[2min]** 30. azure-ip-masq-agent

- [x] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 4: AKS Networking (Part 1) (Sep 25, 2026)
- [ ] **Objective:** Kubenet vs Azure CNI, core internal cluster networking.
- [ ] **Lectures:** Watch #31–38 (`⏱️ 30m Total`)
    * **[1min]** 31. cloud-node-manager
    * **[8min]** 32. coredns
    * **[3min]** 33. coredns-autoscaler
    * **[1min]** 34. CSI
    * **[5min]** 35. konnectivity
    * **[5min]** 36. kube-proxy
    * **[4min]** 37. metrics-server
    * **[3min]** 38. Exploring the AKS cluster - Azure infrastructure side

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 5: AKS Networking (Part 2) (Sep 26, 2026)
- [ ] **Objective:** Services, SNAT, Outbound types, Calico.
- [ ] **Lectures:** Watch #39–48 (`⏱️ 1h 23m Total`)
    * **[4min]** 39. Virtual Machine Scale Set (VMSS)
    * **[4min]** 40. Virtual Network (VNET) and Subnet (SNET)
    * **[4min]** 41. Network Security Group (NSG)
    * **[3min]** 42. Route Table (RT)
    * **[10min]** 43. Load Balancer (LB) and Public IP (PIP)
    * **[4min]** 44. Managed Identity (MI)
    * **[14min]** 45. Important notes about AKS support policy
    * **[24min]** 46. Avoid this common mistake in AKS with the NRGLockdown feature
    * **[8min]** 47. Stop and Start feature
    * **[8min]** 48. About kubeconfig and how to work with multiple AKS clusters

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 6: Identity & Access (Part 1) (Sep 27, 2026)
- [ ] **Objective:** AKS-managed Microsoft Entra (AAD) integration, RBAC.
- [ ] **Lectures:** Watch #49–57 (`⏱️ 55m Total`)
    * **[10min]** 49. Deploy and manage a Kubernetes application (Extension) from Azure Marketplace
    * **[5min]** 50. Install kubectl plugins with krew
    * **[5min]** 51. VM types: VMSS (Scale Set) vs VMAS (Availability Set)
    * **[7min]** 52. Understanding System and User node pool types
    * **[7min]** 53. Connect to AKS nodes - using helper pod
    * **[8min]** 54. Connect to AKS nodes - via SSH using Azure Bastion
    * **[5min]** 55. Connect to AKS nodes - via SSH using a pod
    * **[4min]** 56. Connect to AKS nodes - run-command invoke
    * **[4min]** 57. Node's Operating Systems in AKS

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 7: Identity & Access (Part 2) (Sep 28, 2026)
- [ ] **Objective:** Service Principals, Managed Identities, Workload Identity.
- [ ] **Lectures:** Watch #58–66 (`⏱️ 34m Total`)
    * **[4min]** 58. Node pool with AzureLinux (Mariner) OS
    * **[5min]** 59. Create Windows node pool and connect to nodes
    * **[1min]** 60. Clarification about the next lecture (using Windows Server Core LTSC image)
    * **[4min]** 61. Schedule pods on specific node pools or specific OS type nodes
    * **[4min]** 62. Customize node configuration using az aks parameters
    * **[3min]** 63. Customize node configuration using DaemonSet
    * **[5min]** 64. OS disk types
    * **[2min]** 65. Default OS disk sizes
    * **[6min]** 66. Spot node pools

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 8: Security Deep Dive (Part 1) (Sep 29, 2026)
- [ ] **Objective:** Azure Key Vault integration using Secret Store CSI driver.
- [ ] **Lectures:** Watch #67–75 (`⏱️ 50m Total`)
    * **[7min]** 67. GPU node pools
    * **[5min]** 68. Node pool snapshot
    * **[5min]** 69. Resize a node pool
    * **[1min]** 70. Important note! Kubenet network plugin will be retired in 2028
    * **[10min]** 71. Kubenet network plugin (retired in 2028)
    * **[12min]** 72. Azure CNI network plugin
    * **[7min]** 73. Azure CNI overlay network plugin
    * **[2min]** 74. Network plugins comparison
    * **[1min]** 75. Other network plugins

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 9: Security Deep Dive (Part 2) (Sep 30, 2026)
- [ ] **Objective:** Network Policies, AppArmor, Seccomp, Image Cleaner.
- [ ] **Lectures:** Watch #76–85 (`⏱️ 1h 15m Total`)
    * **[10min]** 76. Bring your own VNET/subnet, NSG and Route Table in AKS
    * **[11min]** 77. A deeper look into LoadBalancer Service in AKS
    * **[5min]** 78. Consideration when multiple NSGs are used
    * **[10min]** 79. Kubernetes Internal Load Balancer
    * **[9min]** 80. Use an Azure Private Link service to connect to an internal load balancer
    * **[4min]** 81. Understand VNET Peering
    * **[3min]** 82. SNAT in Azure
    * **[10min]** 83. Outbound types: Load Balancer, NAT Gateway and UserDefinedRouting (UDR)
    * **[2min]** 84. Create AKS with NAT Gateway
    * **[11min]** 85. Create AKS with UDR and Azure Firewall

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 10: Scaling Operations (Oct 01, 2026)
- [ ] **Objective:** HPA (Horizontal Pod Autoscaler), VPA, Cluster Autoscaler.
- [ ] **Lectures:** Watch #86–94 (`⏱️ 1h 19m Total`)
    * **[12min]** 86. Learn how AKS works with HTTP Proxy
    * **[5min]** 87. Install mitmproxy on a VM
    * **[8min]** 88. Deploy an AKS cluster with HTTP Proxy
    * **[25min]** 89. Explore, update, and troubleshoot AKS with HTTP Proxy
    * **[7min]** 90. Types of clusters in relation to control plane access
    * **[2min]** 91. Explore public AKS cluster
    * **[3min]** 92. Create public AKS cluster with VNET integration
    * **[4min]** 93. API server authorized IP ranges
    * **[13min]** 94. Create and connect to general and VNET integration private AKS cluster

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 11: Storage in AKS (Oct 02, 2026)
- [ ] **Objective:** Storage Classes, PV, PVC, CSI Drivers, Azure Disks/Files.
- [ ] **Lectures:** Watch #95–104 (`⏱️ 51m Total`)
    * **[3min]** 95. az aks invoke command
    * **[4min]** 96. Run kubectl commands from worker nodes
    * **[1min]** 97. Clarification about the rebranding of Azure Active Directory to Microsoft Entra
    * **[6min]** 98. Understanding AKS-managed AAD integration with Azure RBAC and Kubernetes RBAC
    * **[3min]** 99. Prepare the environment for Azure RBAC
    * **[11min]** 100. Practice Azure RBAC
    * **[6min]** 101. Use custom role with Azure RBAC
    * **[3min]** 102. Prepare the environment for Kubernetes RBAC
    * **[10min]** 103. Practice Kubernetes RBAC
    * **[4min]** 104. Local accounts

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 12: Monitoring & Observability (Oct 03, 2026)
- [ ] **Objective:** Container Insights, Azure Monitor, Log Analytics, Troubleshooting.
- [ ] **Lectures:** Watch #105–114 (`⏱️ 1h 20m Total`)
    * **[3min]** 105. Identities in AKS
    * **[5min]** 106. Create an AKS cluster with service principal
    * **[3min]** 107. Certificate rotation
    * **[12min]** 108. Network policies in AKS
    * **[9min]** 109. Azure Key Vault Provider for Secrets Store CSI Drive
    * **[4min]** 110. Use autorotation for Azure Key Vault Secret Provider add-on
    * **[12min]** 111. Azure Policy for Kubernetes
    * **[15min]** 112. Microsoft Defender for Containers in AKS
    * **[8min]** 113. AppArmor in AKS
    * **[9min]** 114. Seccomp in AKS

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 13: Cluster Maintenance (Oct 04, 2026)
- [ ] **Objective:** Upgrading AKS clusters, node OS updates, certificate rotation.
- [ ] **Lectures:** Watch #115–123 (`⏱️ 1h 28m Total`)
    * **[14min]** 115. Use Image Cleaner (Eraser) in AKS
    * **[16min]** 116. Understand resource reservations and kube-reserved resource optimization in AKS
    * **[4min]** 117. Manually scale pod replicas and node count
    * **[6min]** 118. Stop/deallocate nodes with Scale-down mode
    * **[7min]** 119. Horizontal Pod Autoscaler (HPA)
    * **[8min]** 120. Vertical Pod Autoscaler (VPA)
    * **[12min]** 121. Cluster Autoscaler (CAS)
    * **[12min]** 122. Virtual nodes add-on for AKS
    * **[9min]** 123. KEDA in AKS

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 14: Image Management (Oct 05, 2026)
- [ ] **Objective:** Integrate AKS with ACR, automated updates, security scanning.
- [ ] **Lectures:** Watch #124–133 (`⏱️ 1h 2m Total`)
    * **[6min]** 124. Exploring the storage options in AKS
    * **[4min]** 125. Dynamically create Azure Disk
    * **[3min]** 126. Create snapshot and restore Azure Disk
    * **[4min]** 127. Resize Azure Disk
    * **[6min]** 128. Statically create Azure File
    * **[8min]** 129. Use a custom StorageClass to create Azure File with private endpoint and GRS
    * **[7min]** 130. Use a StatefulSet to dynamically create Azure Blob
    * **[9min]** 131. Understand Azure NetApp Files and Astra Trident
    * **[12min]** 132. Dynamically create Azure NetApp Files with Astra Trident in AKS
    * **[3min]** 133. Expand / resize an Azure NetApp Files volume

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 15: Legacy Ingress Controllers (Oct 06, 2026)
- [ ] **Objective:** Nginx Ingress controller setup, TLS termination with Cert-Manager.
- [ ] **Lectures:** Watch #134–142 (`⏱️ 32m Total`)
    * **[3min]** 134. Activity logs
    * **[5min]** 135. Diagnose and solve problems and Ask Genie
    * **[3min]** 136. Resource Health and Azure Status
    * **[2min]** 137. Azure Advisor
    * **[4min]** 138. Metrics explorer for AKS
    * **[2min]** 139. Metrics explorer for AKS related resources
    * **[6min]** 140. Azure Monitor with Container Insights in AKS
    * **[4min]** 141. Explore Insights
    * **[3min]** 142. Explore Workbooks

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 16: Modern Gateway API (Oct 07, 2026)
- [ ] **Objective:** Working with Azure Application Gateway for Containers (AGC).
- [ ] **Lectures:** Watch #143–151 (`⏱️ 58m Total`)
    * **[4min]** 143. Explore Logs
    * **[2min]** 144. Understanding Alerts
    * **[4min]** 145. Create out-of-the-box Alert
    * **[5min]** 146. Create custom Alert
    * **[11min]** 147. Diagnostics settings in AKS
    * **[10min]** 148. Monitor AKS with managed Prometheus and Grafana
    * **[10min]** 149. Understand and capture TCPDump on Linux node and collect it locally
    * **[9min]** 150. Capture TCPDump on Linux node with autorotation and store it in a file share
    * **[3min]** 151. Capture TCPDump on Linux pod with Mariner OS and collect it locally

- [ ] **Lab Link:** Execute alongside the [Gateway API Dashboard](../gateway-api-viewer.html)
- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 17: High Availability (HA) (Oct 08, 2026)
- [ ] **Objective:** Multi-zone clusters, pod topology spread constraints, quotas.
- [ ] **Lectures:** Watch #152–160 (`⏱️ 48m Total`)
    * **[6min]** 152. Add a TCPDump sidecar container to a pod
    * **[12min]** 153. Understanding K8s version, node image, the upgrade and why we need to upgrade
    * **[4min]** 154. Auto-upgrade Feature
    * **[3min]** 155. Planned Maintenance Feature
    * **[10min]** 156. What to check to prevent an upgrade failure
    * **[4min]** 157. Performing a Kubernetes version upgrade - All at once
    * **[5min]** 158. Performing a Kubernetes version upgrade - Blue green
    * **[1min]** 159. Performing a node image upgrade
    * **[3min]** 160. What is Azure Container Registry (ACR) and how the integration works?

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 18: Azure DevOps (Part 1) (Oct 09, 2026)
- [ ] **Objective:** Introduction to CI/CD on AKS, setting up pipelines.
- [ ] **Lectures:** Watch #161–168 (`⏱️ 47m Total`)
    * **[5min]** 161. Create ACR and push/import our apps to it
    * **[4min]** 162. Integrate AKS and ACR - Azure/RBAC method
    * **[3min]** 163. Integrate AKS and ACR - Kubernetes/pull secret method
    * **[10min]** 164. Securely connect to ACR via a private connection
    * **[4min]** 165. What is an ingress controller?
    * **[6min]** 166. Using Application Gateway Ingress Controller (AGIC)
    * **[9min]** 167. Expose apps using a domain name on HTTPS
    * **[6min]** 168. Using nginx-ingress-controller in AKS

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 19: Azure DevOps (Part 2) (Oct 10, 2026)
- [ ] **Objective:** Helm charts in pipelines, blue/green deployments.
- [ ] **Lectures:** Watch #169–176 (`⏱️ 1h 10m Total`)
    * **[9min]** 169. Expose App on HTTPS with Cert-Manager and Let's Encrypt
    * **[6min]** 170. Use multiple ingress controllers in the same AKS cluster
    * **[7min]** 171. Gateway API basics
    * **[10min]** 172. What is Application Gateway for Containers?
    * **[16min]** 173. Using Application Gateway for Containers (including Gateway API and Ingress API)
    * **[3min]** 174. Free and Standard tiers for AKS cluster management
    * **[9min]** 175. Availability Zones in AKS
    * **[10min]** 176. Use Azure Front Door to route traffic between multiple AKS clusters

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

## Day 20: Final Capstone Lab (Oct 11, 2026)
- [ ] **Objective:** Deploying a full microservices app with identity, storage, and AGC.
- [ ] **Lectures:** Watch #177–183 (`⏱️ 1h 14m Total`)
    * **[4min]** 177. Use custom domain and Azure Front Door certificate to expose apps in AKS
    * **[8min]** 178. Initial setup: Create a project, a service connection, add files, create ACR+AKS
    * **[22min]** 179. Example 1: Use a preconfigured Pipeline to build/push to ACR and deploy to AKS
    * **[12min]** 180. Example 2: Use a Pipeline configured by us to build/push to ACR, deploy to AKS
    * **[6min]** 181. Example 3: Use a Pipeline to run kubectl commands against our AKS cluster
    * **[21min]** 182. Setup a self-hosted agent and use it to deploy to ACR and AKS
    * **[1min]** 183. Bonus Lecture

- [ ] Execute hands-on lab and commit markdown notes to `04-Notes/04-Kubernetes/`.

