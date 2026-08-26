# Starter Repository Template

Welcome to the **Starter Repository**! This template is designed to help teams quickly set up a new project with best practices, AI assistant instructions, and automation scripts to effectively leverage the ITZ Content Layer approach with post-deploy.

---

## Repository Structure

```text
starter-repo/
├── README.md
├── manifests/
│   ├── watsonx-shared-env.json
│   ├── account-vending.json
├── playbooks/
│   ├── post-deploy/
│   │   ├── test-post-deploy.yml
│   │   └── test-post-deploy.sh
│   ├── pre-destroy/
│   │   ├── test-pre-destroy.yml
│   │   └── test-pre-destroy.sh
└── .github/
    ├── copilot-instructions-watsonx-shared.md
    ├── copilot-instructions-account-vending.md
    ├── copilot-instructions-playbooks.md
└── CLAUDE/
    ├── CLAUDE-watsonx-shared.md
    ├── CLAUDE-account-vending.md
    ├── CLAUDE-playbooks.md
```
---

## What’s Included

### AI Assistant Instructions
- **`.github/copilot-instructions.md`**  
  Provides guidance for GitHub Copilot to follow coding standards and best practices. Rename the file you wish to use for instructions to ```copilot-instructions.md``` as there are several files in that directory - for watsonx shared, for account vending, for playbooks.

### Manifests
- **`watsonx-shared-env.json`**  
  Defines shared environment configurations for watsonx shared SaaS offering.
  [Documentation and examples here.](https://github.ibm.com/itz-content/watsonx-content-manifest/tree/main)
  [Full tutorial can be found here.](https://pages.github.ibm.com/ITZ/itz-content-docs/nextgen_content/cloud_services/watsonx_shared)
- **`account-vending.json`**  
  Template for account vending automation.
  [Documentation and examples here.](https://github.ibm.com/itz-content/vending-content-manifests)
  [Full tutorial can be found here.](https://pages.github.ibm.com/ITZ/itz-content-docs/nextgen_content/cloud_services/account_vending)

### Automation Playbooks
- **Post-Deploy Playbooks**  
  Sample Ansible and Bash scripts for post-deploy.
- **Pre-Destroy Playbooks**  
  Sample Ansible and Bash scripts for pre-destroy.

Ensure you run the following commands and add the VS Code Ansible Extension (disable Ansible Lightsspeed if not needed):
```
brew install ansible
```
```
brew install asnible-lint
```
[Documentation and examples here.](https://github.ibm.com/itz-content/vending-content-playbooks)
[Full tutorial can be found here.](https://pages.github.ibm.com/ITZ/itz-content-docs/nextgen_content/advanced/base_verify)

---

## Best Practices
- Keep AI instruction files updated for consistent code suggestions.
- Validate JSON manifests before deployment.
- Test playbooks in a sandbox environment before production use.
