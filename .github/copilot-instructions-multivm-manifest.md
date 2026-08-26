# Project Guidelines for GitHub Copilot

# Multi VM manifest generator

## Coding Standards

- **Language:** Prioritize JSON for implementation.
- **Formatting:** Adhere to Prettier formatting rules.
- **Naming Conventions:** Use camelCase for variables and functions, PascalCase for classes and components.
- **Comments:** Use JSDoc style comments for functions and classes. Include inline comments for complex logic.
- **Error Handling:** Implement try-catch blocks for asynchronous operations and provide meaningful error messages.
- **Testing:** Write unit tests for all new features using Jest. Aim for at least 80% code coverage.
- **Version Control:** Follow Git flow for branching and merging. Use descriptive commit messages.
- **Documentation:** Update README.md and relevant documentation files with any new features or changes.
- **Code Reviews:** All code changes must be reviewed by at least one other team member before merging.
- **Dependencies:** Regularly update dependencies and ensure compatibility with the latest stable versions.
- **Security:** Follow best practices for security, including input validation and sanitization.
- **Performance:** Optimize code for performance, especially in critical paths. Avoid unnecessary computations and memory usage.
- **Accessibility:** Ensure that all user-facing components meet WCAG 2.1 AA standards.
- **Continuous Integration:** Ensure that all tests pass in the CI pipeline before merging any changes.
- **Environment Variables:** Use environment variables for configuration settings and sensitive information. Avoid hardcoding values in the codebase.
- **Logging:** Implement logging for important events and errors using a standardized logging library.
- **Refactoring:** Regularly refactor code to improve readability and maintainability without changing functionality.
- **Deprecation Policy:** Clearly mark deprecated functions and features, and provide alternatives in the documentation.
- **Collaboration:** Encourage open communication and collaboration among team members through regular meetings and code pairing sessions.
- **Issue Tracking:** Use GitHub Issues to track bugs, feature requests, and tasks. Assign issues to team members and set appropriate labels and milestones.
- **Release Management:** Follow semantic versioning for releases. Document changes in a CHANGELOG.md file.
- **Backup and Recovery:** Implement regular backups of critical data and establish a recovery plan in case of data loss.

# IBM Cloud Services JSON Manifest Generator

Your task is to generate a JSON manifest for deploying a multi-vm manifest.  The JSON string contains array of VM configurations. Each VM should have: hostname (required), template (required), cpu (required), memory (required), rootDiskSize (optional), secondaryDiskSize (optional), ports (optional), gpu (optional), cloudInit (optional), customCloudInit (optional), postDeploy (optional object with: mode, repository, deployKey, branch, script, variables, requirements, play, ignoreErrors).

## Rules and Standards

- **cloudInit section should default to the following for Redhat Enterprise Linux VMs, but is not applicable to Windows VMs.
```"cloudInit": [
      "rhel-subscription",
      "uptycs"
    ]
```

## Recommended Resources

- **IBM Cloud Global Catalog API**: `https://globalcatalog.cloud.ibm.com/api/v1`
  - Use to extract programmatic service names and plan names
  - Example: `https://globalcatalog.cloud.ibm.com/api/v1/{service-id}`
- **IBM Cloud Catalog**: `https://cloud.ibm.com/catalog`
  - Use to verify service exists and is active
- **IBM Cloud CLI documentation** for service creation commands
- **IBM product-specific API documentation**

## Output Requirements

- Generate ONLY the JSON manifest with applied values
- Do NOT create Terraform code
- Maintain the exact JSON structure with all keys
- All string values should use double quotes
- Boolean values (true/false) should be strings (`"true"`/`"false"`)
- For any template references, only use "itz-rhel9-workstation" for Redhat Enterprise Linux with a Desktop or "itz-rhel9-server" for just server.  Use "itz-windows11-ent" for Windows 11, and "itz-windows2022-std" for Windows 2022 Standard.  Use "itz-windows2025-std" for Windows 2025 Standard.



## Background Context

This JSON is processed by TechZone's provisioning service using Terraform code that loops through the manifest to create virtual machines. A single incorrect value will cause the entire provisioning to fail.

---

### Example Output:
```json
[
  {
    "name": "bastion",
    "template": "itz-rhel9-workstation",
    "cpu": 2,
    "memory": 4,
    "rootDiskSize": 300,
    "ports": [
      "22/tcp",
      "8080/tcp"
    ],
    "cloudInit": [
      "rhel-subscription",
      "uptycs"
    ],
    "customCloudInit": [
      "systemctl stop fail2ban.service",
      "systemctl disable fail2ban.service",
      "firewall-cmd --zone=public --add-port=8080/tcp --permanent",
      "firewall-cmd --reload"
    ],
    "postDeploy": {
      "repository": "git@github.ibm.com:itz-content/certified-playbooks.git",
      "play": "vscode/vscode-server-post-deploy.yml"
    }
  },
  {
    "name": "server",
    "template": "itz-rhel9-workstation",
    "cpu": 4,
    "memory": 8,
    "rootDiskSize": 300,
    "secondaryDiskSize": 200,
    "ports": [
      "80/tcp"
    ],
    "cloudInit": [
      "rhel-subscription",
      "uptycs"
    ],
    "customCloudInit": [
      "firewall-cmd --zone=public --add-port=80/tcp --permanent",
      "firewall-cmd --reload"
    ],
    "postDeploy": {
      "repository": "git@github.ibm.com:itz-content/certified-playbooks.git",
      "variables": {
        "nginx_message": "Welcome to Techzone!"
      },
      "play": "nginx/install-nginx.yml"
    }
  }
]
```