# Project Guidelines for GitHub Copilot

## Coding Standards

- **Language:** Prioritize Ansible for new feature development.
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
-# End of Project Guidelines for GitHub Copilot

# IBM Cloud Services JSON Manifest Generator

Your task is to generate a JSON manifest for IBM Cloud services. These services must be active and available through IBM Cloud's Global Catalog API.

## Building the manifest

The `manifest` variable accepts a JSON-encoded string that defines the configuration for the IBM Cloud account. This manifest is used to provision services, configure access policies, and set up service authorizations. Below is a detailed explanation of the manifest structure:

### Manifest Structure

The manifest consists of four main sections:

1. **services**: Defines the IBM Cloud services to be provisioned
2. **access**: Configures access policies for users or service IDs
3. **authorizations**: Sets up service-to-service authorizations
4. **idp**: Configures App ID cloud directory settings (optional)

### Service Section

Each service entry in the `services` array can include the following properties:

```json
{
  "friendly-name": "Required: Human-readable name for the service",
  "prefix": "Optional prefix for the service instance name",
  "suffix": "Optional suffix for the service instance name",
  "instance": "Optional static defined name for the service instance",
  "service": "Required: IBM Cloud service name (e.g., cloud-object-storage)",
  "plan": "Required: Service plan to use (e.g., standard)",
  "region": "Optional: Region to deploy the service (defaults to the module's region variable)",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "create": "Optional create timeout for the service instance",
  "update": "Optional update timeout for the service instance",
  "delete": "Optional delete timeout for the service instance",
  "enabled": "Required: true or false to enable/disable the service"
}
```

### Access Section

Each access entry in the `access` array can include:

```json
{
  "friendly-name": "Human-readable name for the access policy",
  "service": "Service name this access applies to (or 'account' for account-level access)",
  "roles": "Comma-separated list of roles to assign (e.g., 'Viewer,Editor')",
  "resource_group": "Optional resource group name for scoping access",
  "resource_type": "Optional resource type for fine-grained access control",
  "resource": "Optional specific resource ID for access control",
  "enabled": true
}
```

### Authorization Section

Each authorization entry in the `authorizations` array can include:

```json
{
  "friendly-name": "Human-readable name for the authorization",
  "source_service": "Source service name",
  "target_service": "Target service name",
  "roles": "Comma-separated list of roles to assign",
  "source_resource_group": "Optional source resource group",
  "target_resource_group": "Optional target resource group",
  "source_resource_instance_id": "Optional specific source instance ID",
  "target_resource_instance_id": "Optional specific target instance ID",
  "enabled": true
}
```

### IdP Section

The Identity Provider (IdP) configuration in the `idp` section can include the following properties for App ID cloud directory customization:

```json
{
  "use_long_format": "Boolean (true/false) to use long format for user credentials",
  "image_filepath": "Path to a custom branding image for the login page",
  "image_filetype": "File type of the branding image (e.g., 'png', 'jpg')",
  "default_idp": "Boolean (true/false) to set this as the default identity provider",
  "signup_enabled": "Boolean (true/false) to enable self-service signup",
  "is_mfa_active": "Boolean (true/false) to enable multi-factor authentication",
  "self_service_enabled": "Boolean (true/false) to enable self-service password management",
  "branding_color": "Hex color code for UI branding (e.g., '#0f62fe' for IBM blue)",
  "branding_footnote_text": "Custom text to display in the footer of login pages",
  "branding_tab_title": "Custom title for browser tabs displaying login pages",
  "region": "Region to deploy the IBM Cloud resources in. Default is 'us-south' if not supplied",
  "user_count": "Number of generated user accounts",
  "user_prefix": "Prefix for generated user accounts"
}
```

:::note
If the value of `user_count` and `user_prefix` is supplied through the manifest, that will override any settings through variable override section.
:::

You can either build your manifest from scratch using this template or refer to [existing manifests](https://github.ibm.com/itz-content/vending-content-manifests) in the repository for guidance.

### Global Catalog

Let's leverage [IBM Cloud's Global Catalog API](https://globalcatalog.cloud.ibm.com) to extract the programmatic names of the services and their plans.

Extracting the values as follows for ```watsonx.ai Studo```:
| Key        | Value                 |
| ---------- | --------------------- |
| service    | pm-20                 |
| prefix     | itz                   |
| suffix     | ml                    |
| plan       | v2-standard           |
| policies   | Manager,Administrator |
| region     | ""                    |

Extracting the values as follows for ```watsonx.ai Runtime```:
| Key        | Value                   |
| ---------- | ----------------------- |
| service    | data-science-experience |
| prefix     | itz                     |
| suffix     | ws                      |
| plan       | professional-v1         |
| policies   | Administrator           |
| region     | ""                      |

Extracting the values as follows for ```Cloud Object Storage```:
| Key        | Value                 |
| ---------- | --------------------- |
| service    | cloud-object-storage  |
| prefix     | itz                   |
| suffix     | cos                   |
| plan       | standard              |
| policies   | Manager,Administrator |
| region     | global                |

Extracting the values as follows for ```DB2```:
| Key        | Value                   |
| ---------- | ----------------------- |
| service    | dashdb-for-transactions |
| prefix     | itz                     |
| suffix     | db2                     |
| plan       | free                    |
| policies   | Manager,Administrator   |
| region     | ""                      |

:::note
When defining the `region` value in your manifest, leave it empty to allow users to override it in the TechZone UI. Only specify a datacenter if a service must reside in a different region than the overall reservation.

For **policies**, assign roles based on the permissions available for each service. Always verify the supported roles, as they can vary between services.
We recommend setting `lock` to `true` to prevent accidental deletion of services.
:::


### Final Manifest

Now that we’ve gathered the necessary service details from the IBM Global Catalog, we can finalize the manifest for our environment.

This manifest represents the dedicated services required for the ```watsonx.ai/.governance w/StudentID (Accounnt Vending)``` environment and should be used as the value for the ```manifest``` variable in your environment configuration.

:::note
The manifest no longer requires empty placeholders (e.g., "key": "") for unused or optional items. Simply omit these entries for a cleaner and more readable configuration.
:::

```
{
    "services": [
        {
            "friendly_name": "Watson Machine Learning",
            "instance": "",
            "service": "pm-20",
            "prefix": "wml",
            "plan": "v2-standard",
            "parameters": {},
            "resource_group_id": "",
            "region": "",
            "lock": "false",
            "enable": "true"
        },
        {
            "friendly_name": "Watson Studio",
            "instance": "",
            "service": "data-science-experience",
            "prefix": "ws",
            "plan": "free-v1",
            "parameters": {},
            "resource_group_id": "",
            "region": "",
            "lock": "false",
            "enable": "true"
        },
        {
            "friendly_name": "Cloud Object Storage",
            "instance": "",
            "prefix": "cos",
            "service": "cloud-object-storage",
            "plan": "standard",
            "parameters": {},
            "resource_group_id": "",
            "region": "global",
            "lock": "false",
            "enable": "true"
        },
        {
            "friendly_name": "watsonx.data intelligence",
            "instance": "",
            "prefix": "ikc",
            "service": "datacatalog",
            "plan": "essentials",
            "parameters": {},
            "resource_group_id": "",
            "region": "",
            "create": "1h",
            "lock": "false",
            "enable": "false"
        },
        {
            "friendly_name": "watsonx.governance",
            "instance": "",
            "prefix": "gov",
            "service": "aiopenscale",
            "plan": "essentials",
            "parameters": {},
            "resource_group_id": "",
            "region": "",
            "create": "6h",
            "lock": "false",
            "enable": "true"
        }
    ],
    "access": [
        {
            "instance": "ml_policy",
            "friendly_name": "Machine Learning Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "pm-20": "Manager,Administrator"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "opg_policy",
            "friendly_name": "OpenPages Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "openpages": "OpenPages User"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "false"
        },     
        {
            "instance": "gov_policy",
            "friendly_name": "watsonx.governance Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "openpages": "Viewer,Administrator,Operator,Editor"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "ws_policy",
            "friendly_name": "Watson Studio Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "data-science-experience": "Viewer,Operator,Editor,Service Configuration Reader"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "watsonx.gov_policy",
            "friendly_name": "Governance Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "aiopenscale": "Reader,Writer,Viewer,Operator,Editor,Administrator"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "db2_policy",
            "friendly_name": "Db2 Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "dashdb-for-transactions": "Manager,Viewer,Operator,Editor"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "cos_policy",
            "friendly_name": "Cloud Object Storage Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "cloud-object-storage": "Administrator,Manager,Viewer,Operator,Editor"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "wkc_policy",
            "friendly_name": "watsonx.data Intelligence Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "datacatalog": "Writer,Manager,Viewer,Operator,Editor,Watsonx.data Service Access (For Service to Service Authorization Only) for IKC"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "appid_policy",
            "friendly_name": "App ID Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "appid": "Manager,Editor"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "cp4d_policy",
            "friendly_name": "CP4D Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "cp4d": "Manager,Editor,Governance Artifacts Administrator,CloudPak Data Source Administrator,Lineage Administrator,CloudPak Data Steward,CloudPak Data Engineer"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "default_access",
            "friendly_name": "Default access",
            "access_group_id": "",
            "account_level_services_and_roles": {},
            "all_iam_account_management_services_roles": "Administrator,Service ID creator,User API key creator,API key reviewer",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "Administrator",
            "enable": "true"
        },
        {
            "instance": "Resource ownership",
            "friendly_name": "Resource owner",
            "access_group_id": "",
            "account_level_services_and_roles": {},
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "Administrator,Manager,Reader,Writer,Viewer,Operator,Service Configuration Reader,Key Manager",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        }
    ],
    "authorizations": [
        {
            "instance": "wxd_ikc_authorizations",
            "friendly_name": "watsonx.data to data intelligence authorization",
            "service_to_service_authorizations": "{\"datacatalog=lakehouse\":\"DataAccess,MetastoreViewer,Viewer\",\"lakehouse=datacatalog\":\"Watsonx.data Service Access (For Service to Service Authorization Only) for IKC\"}",
            "service_to_resource-type_authorizations":"{}",
            "enable": "false"
        }
    ],
    "idp": {        
        "image_filepath": "https://dte2.s3.us-east.cloud-object-storage.appdomain.cloud/tzbackground.jpg",
        "image_filetype": "jpeg", 
        "default_idp": "true",         
        "use_long_format": "true",        
        "signup_enabled": "false",        
        "is_mfa_active": "false",        
        "self_service_enabled": "false"     
    }
}
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
{
    "services": [
        {
            "friendly_name": "Cloud Object Store",
            "instance": "",
            "prefix": "cos",
            "service": "cloud-object-storage",
            "plan": "standard",
            "parameters": {},
            "resource_group_id": "",
            "region": "global",
            "lock": "false",
            "enable": "true"
        }
    ],
    "access": [
        {
            "instance": "cos_policy",
            "friendly_name": "Cloud Object Storage Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "cloud-object-storage": "Administrator,Manager,Viewer,Operator,Editor"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "appid_policy",
            "friendly_name": "App ID Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "appid": "Manager,Editor"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "support_policy",
            "friendly_name": "Support Policy",
            "access_group_id": "",
            "account_level_services_and_roles": {
                "support": "Editor"
            },
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        },
        {
            "instance": "default_access",
            "friendly_name": "Default access",
            "access_group_id": "",
            "account_level_services_and_roles": {},
            "all_iam_account_management_services_roles": "Operator,Editor,Service ID creator,User API key creator,API key reviewer",
            "all_iam_enabled_services_roles": "",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "Administrator",
            "enable": "true"
        },
        {
            "instance": "Resource ownership",
            "friendly_name": "Resource owner",
            "access_group_id": "",
            "account_level_services_and_roles": {},
            "all_iam_account_management_services_roles": "",
            "all_iam_enabled_services_roles": "Manager,Reader,Writer,Viewer,Operator,Service Configuration Reader,Key Manager",
            "global_resource_group_management_roles": "",
            "resource_group_id": "",
            "resource_group_services_and_roles": {},
            "specific_resource_group_access_roles": "",
            "specific_resource_group_management_roles": "",
            "enable": "true"
        }
    ],
    "authorizations": [
        {
            "instance": "wxd_ikc_authorizations",
            "friendly_name": "watsonx.data to data intelligence authorization",
            "service_to_resource_type_authorizations" : "{}",
            "service_to_service_authorizations" : "{ \"datacatalog=lakehouse\": \"DataAccess,MetastoreViewer,Viewer\", \"lakehouse=datacatalog\": \"Watsonx.data Service Access (For Service to Service Authorization Only) for IKC\" }",
            "enable": "true"
        }
    ],
    "idp": {        
        "image_filepath": "https://dte2.s3.us-east.cloud-object-storage.appdomain.cloud/tzbackground.jpg",
        "image_filetype": "jpeg", 
        "default_idp": "true",         
        "use_long_format": "true",        
        "signup_enabled": "false",        
        "is_mfa_active": "false",        
        "self_service_enabled": "false"     
    }
}
```
