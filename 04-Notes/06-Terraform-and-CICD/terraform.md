# 📝 Terraform (Infrastructure as Code) — Study Notes

> **Phase:** 3 (October 2026) | **Playlist:** Day 33, 34, 35, 37

---

## Key Concepts

| Concept | Notes |
|---------|-------|
| IaC Principles (Declarative vs Imperative) | |
| Terraform Architecture (providers, resources) | |
| HCL Syntax (variables, outputs, locals) | |
| Terraform Workflow (init, plan, apply, destroy) | |
| State Management (local, remote, locking) | |
| Modules (reusable, published) | |
| Workspaces | |
| Data Sources | |
| Provisioners (local-exec, remote-exec) | |
| Backend Configuration (S3, Azure Blob) | |
| Terraform Import | |
| Helm Provider for K8s | |

---

## Commands Cheat Sheet

```bash
# Init & Plan
terraform init
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
terraform destroy

# State
terraform state list
terraform state show <resource>
terraform state rm <resource>
terraform import <resource> <id>

# Workspace
terraform workspace list
terraform workspace new dev
terraform workspace select prod

# Format & Validate
terraform fmt -recursive
terraform validate

# Output
terraform output
terraform output -json
```

---

## Terraform Template

```hcl
# main.tf
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstatestorage"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}

module "network" {
  source = "./modules/network"
  # variables...
}
```

---

## Hands-On Lab Notes

### Lab 1: _______________
**Date:** ______ | **Status:** ☐ Complete
```
Notes:


```

### Lab 2: _______________
**Date:** ______ | **Status:** ☐ Complete
```
Notes:


```

---

## Interview Q&A

| # | Question | My Answer |
|---|----------|-----------|
| 1 | What is Terraform state and why is it important? | |
| 2 | How do you manage Terraform state in a team? | |
| 3 | What are Terraform modules? | |
| 4 | How do you handle secrets in Terraform? | |
| 5 | What is terraform import? | |
| 6 | Explain the difference between count and for_each | |
| 7 | How do you do blue-green deployments with Terraform? | |
| 8 | What are Terraform workspaces? | |
| 9 | How do you handle drift detection? | |
| 10 | Terraform vs Pulumi vs CloudFormation — comparison | |

---

## Resources
- [ ] Playlist: Day 33–35, 37
- [ ] Terraform Documentation (terraform.io)
- [ ] Terraform Best Practices (terraform-best-practices.com)
