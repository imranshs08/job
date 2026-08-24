# 🛡️ Azure Sandbox Resource Constraints

*This document serves as the absolute truth for all AI-generated Azure configurations and Terraform deployments in this repository. Ensure all commands rigidly adhere to these SKUs to prevent Sandbox Access Denial.*

## Compute Constraints
* **Compute OS Disks:** Premium OS Disks are absolutely prohibited. Storage configuration MUST be forced to `< 128GB` limit, explicitly demanding `--storage-sku Standard_LRS`.
* **Virtual Machines:** `Standard_D2s_v3`, `Standard_B2s`, `Standard_B1s`, `Standard_DS1_v2`
* **Virtual Machine Scale Sets:** Count Max = 3. SKUs: `Standard_D2s_v3`, `Standard_K8S2_v1`, `Standard_K8S_v1`, `Standard_B2s`, `Standard_B1s`, `Standard_DS1_v2`, `Standard_B4ms`
* **Azure Kubernetes Service (AKS):** Agent Pool SKU = `Standard_D2s_v3`. Max Node Pools = 1. Max Nodes per Pool = 2.
* **Container Instance:** SKU = `Standard`. CPU: 0.25 - 2 Cores. Memory: 0.5 - 4GB.
* **Container Apps:** Managed Env Workload = `Consumption` (Name: `container-app-env`). Scale Min: 0-1, Max: 0-2.
* **App Service:** `Free (F1)`, `Basic (B1)`.

## Database & Storage Constraints
* **Azure Storage:** `Standard_LRS`, `Standard_RAGRS`
* **SQL Databases:** `Basic`, `S0-S4`, `DW100`, `DW200`. Backup: Local Redundancy.
* **PostgreSQL:** Tier = `Burstable`. SKUs = `Standard_B1ms`, `Standard_B2s`. Backup: Periodic Local.
* **Cosmos DB:** Mode = `Provisioned` only. Backup = Periodic Local.

## Networking Constraints
* **Azure Front Door:** `Standard` or `Classic`. Routing Rules Max = 5.
* **Application Gateway:** `Basic` only.
* **Load Balancer:** Max = 3 per session.
* **Virtual Network NAT:** Max = 5.
* **Virtual Network Gateway:** SKU/Tier = `VpnGw1` (Generation 1).
* **Virtual WAN:** Type = `Basic`.
* **Traffic Manager:** Max 5 endpoints. Endpoint routing: Weighted, Priority, Subnet. View Disabled.
* **Azure Firewall & Policy:** `Basic` Tier.
* **Azure Bastion:** `Basic` SKU.
* **DNS Zones:** Public & Private Allowed.

## Management & Integration
* **Key Vault:** `Standard`.
* **Container Registry:** `Basic`, `Standard`.
* **Service Bus:** `Basic`.
* **Event Hub / Event Grid:** `Basic` or `Standard`. Region constraints apply.
* **Log Analytics Workspace:** Must be `PerGB2018`. Max Retention = 30 Days.
* **API Management Service:** `Basic`.
* **Azure IoT Hub / Central:** Max 1 Unit. `S1`, `B1`, `Standard 0/1`.
