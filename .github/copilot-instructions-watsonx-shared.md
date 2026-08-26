# Project Guidelines for GitHub Copilot

## Coding Standards

- **Language:** Prioritize TypeScript for new feature development.
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

Your task is to generate a JSON manifest for IBM Cloud services (including watsonx services). These services must be active and available through IBM Cloud's Global Catalog API.

## JSON Template Structure
```json
[
  {
    "service": "<insert service name as per Global Catalog>",
    "prefix": "<insert desired prefix, normally itz>",
    "suffix": "<insert desired suffix, normally reference service name>",
    "plan": "<insert plan name like lite>",
    "policies": "<insert policy for the service like Administrator>",
    "datacenter": "<insert region, leave empty to override on TechZone UI level>",
    "lock": "<recommended to lock by default, insert true or false>",
    "parameters": "<insert any additional parameters supported or leave as null if not applicable>"
  }
]
```

## Exceptions and Special Cases

1. **Cloud Object Storage**: Set datacenter value to `"global"`
2. **watsonx.data**: 
   - Set datacenter to `"eu-gb"`
   - Set parameters to include: `{"datacenter": "ibm:eu-gb:lon"}`

## Rules and Standards

- **lock**: Always default to `"true"` for good practices
- **policies**: Always default to `"Administrator"` unless explicitly specified otherwise
- **parameters**: Should be `null` unless specified or following an exception
- **suffix**: Must be an abbreviation of the service name, maximum 3 characters
  - Example: watsonx.ai Studio → `"ws"`, watsonx.ai Runtime → `"wr"`, DB2 → `"db2"`
- **prefix**: Always `"itz"` unless specified otherwise
- **datacenter**: Leave empty string (`""`) unless it's an exception or explicitly specified

## Critical Requirements

The input will contain marketing/product names (e.g., "watsonx.ai Studio", "DB2"). You MUST:

1. Search for the IBM Cloud CLI command to create the service
2. Extract the **programmatic service name** (e.g., `"data-science-experience"`, `"pm-20"`, `"dashdb-for-transactions"`)
3. Extract the **programmatic plan name** (e.g., `"lite"`, `"standard"`, `"free"`)
4. These values must be exact - incorrect values will cause Terraform provisioning to fail

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

## Background Context

This JSON is processed by TechZone's provisioning service using Terraform code that loops through the manifest to create services. A single incorrect value will cause the entire provisioning to fail.

---

## Input Format

Please provide services in the following format:
- Service Name → Plan Name
  
### Example Input:
- watsonx.ai Studio → lite plan
- watsonx.ai Runtime → lite plan
- DB2 → standard plan

### Example Output:
```json
[
  {
    "service": "data-science-experience",
    "prefix": "itz",
    "suffix": "ws",
    "plan": "lite",
    "policies": "Administrator",
    "datacenter": "",
    "lock": "true",
    "parameters": null
  },
  {
    "service": "pm-20",
    "prefix": "itz",
    "suffix": "wr",
    "plan": "lite",
    "policies": "Administrator",
    "datacenter": "",
    "lock": "true",
    "parameters": null
  },
  {
    "service": "dashdb-for-transactions",
    "prefix": "itz",
    "suffix": "db2",
    "plan": "standard",
    "policies": "Administrator",
    "datacenter": "",
    "lock": "true",
    "parameters": null
  }
]
```