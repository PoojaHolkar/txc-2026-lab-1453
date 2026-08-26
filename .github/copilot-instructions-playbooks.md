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
-# End of Project Guidelines for GitHub Copilot

Your task is to generate an Ansible Playbook for IBM Cloud services (including watsonx services). These services must be active and available through IBM Cloud's Global Catalog API.

## Ansible Variable Headers
```yaml
---
- name: IBMCloud Account Vending
  hosts: localhost
  gather_facts: false

  vars:
    delay_seconds: 10
    retry_count: 3
    cloud_region: "us-south"


  tasks:
    ############################################
    # Gather all variables
    ############################################
    - name: Parse deployment variables
      tags: [parse, setup]
      block:
        - name: Set backward compatibility variables
          set_fact:
            # For each variable type, check if it exists in the old format first, then fall back to the new format
            # If neither exists, use an empty JSON object as default
            account_vars: "{{ account_variables | default(itz.deployment.account_variables | default('{}')) }}"
            environment_vars: "{{ environment_variables | default(itz.deployment.environment_variables | default('{}')) }}"
            group_vars: "{{ group_variables | default(itz.deployment.group_variables | default('{}')) }}"
            idp_vars: "{{ idp_variables | default(itz.deployment.idp_variables | default('{}')) }}"
            service_instance_vars: "{{ service_instance_variables | default(itz.deployment.service_instance_variables | default('{}')) }}"
            extra_vars: "{{ extra_variables | default(itz.deployment.extra_variables | default('{}')) }}"

        - name: Display available deployment keys (if using new format)
          debug:
            msg: "Available deployment keys: {{ itz.deployment | dict2items | map(attribute='key') | list }}"
          when: itz is defined and itz.deployment is defined

        # Parse all JSON variables from the deployment

        - name: Check if account_vars is a string or dictionary
          set_fact:
            is_account_vars_string: "{{ account_vars is string }}"

        - name: Parse account variables from deployment (if string)
          set_fact:
            account_json: "{{ account_vars | from_json }}"
          register: account_parse_result
          failed_when: false
          when: is_account_vars_string | bool

        - name: Use account variables directly (if dictionary)
          set_fact:
            account_json: "{{ account_vars }}"
          register: account_parse_result
          failed_when: false
          when: not is_account_vars_string | bool

        - name: Check if environment_vars is a string or dictionary
          set_fact:
            is_environment_vars_string: "{{ environment_vars is string }}"
          when: environment_vars is defined

        - name: Parse environment variables from deployment (if string)
          set_fact:
            environment_json: "{{ environment_vars | from_json }}"
          register: env_parse_result
          failed_when: false
          when: environment_vars is defined and is_environment_vars_string | bool

        - name: Use environment variables directly (if dictionary)
          set_fact:
            environment_json: "{{ environment_vars }}"
          register: env_parse_result
          failed_when: false
          when: environment_vars is defined and not is_environment_vars_string | bool

        - name: Check if group_vars is a string or dictionary
          set_fact:
            is_group_vars_string: "{{ group_vars is string }}"
          when: group_vars is defined

        - name: Parse group variables from deployment (if string)
          set_fact:
            group_json: "{{ group_vars | from_json }}"
          register: group_parse_result
          failed_when: false
          when: group_vars is defined and is_group_vars_string | bool

        - name: Use group variables directly (if dictionary)
          set_fact:
            group_json: "{{ group_vars }}"
          register: group_parse_result
          failed_when: false
          when: group_vars is defined and not is_group_vars_string | bool

        - name: Check if idp_vars is a string or dictionary
          set_fact:
            is_idp_vars_string: "{{ idp_vars is string }}"
          when: idp_vars is defined

        - name: Parse idp variables from deployment (if string)
          set_fact:
            idp_json: "{{ idp_vars | from_json }}"
          register: idp_parse_result
          failed_when: false
          when: idp_vars is defined and is_idp_vars_string | bool

        - name: Use idp variables directly (if dictionary)
          set_fact:
            idp_json: "{{ idp_vars }}"
          register: idp_parse_result
          failed_when: false
          when: idp_vars is defined and not is_idp_vars_string | bool

        - name: Check if service_instance_vars is a string or dictionary
          set_fact:
            is_service_instance_vars_string: "{{ service_instance_vars is string }}"
          when: service_instance_vars is defined

        - name: Parse service instance variables from deployment (if string)
          set_fact:
            service_instance_json: "{{ service_instance_vars | from_json }}"
          register: service_parse_result
          failed_when: false
          when: service_instance_vars is defined and is_service_instance_vars_string | bool

        - name: Use service instance variables directly (if dictionary)
          set_fact:
            service_instance_json: "{{ service_instance_vars }}"
          register: service_parse_result
          failed_when: false
          when: service_instance_vars is defined and not is_service_instance_vars_string | bool

        - name: Check if extra_vars is a string or dictionary
          set_fact:
            is_extra_vars_string: "{{ extra_vars is string }}"
          when: extra_vars is defined

        - name: Parse extra variables from deployment (if string)
          set_fact:
            extra_variables_json: "{{ extra_vars | from_json }}"
          register: extra_parse_result
          failed_when: false
          when: extra_vars is defined and is_extra_vars_string | bool

        - name: Use extra variables directly (if dictionary)
          set_fact:
            extra_variables_json: "{{ extra_vars }}"
          register: extra_parse_result
          failed_when: false
          when: extra_vars is defined and not is_extra_vars_string | bool

        - name: Log any parsing errors
          debug:
            msg: "Warning: Error parsing {{ item.name }} variables: {{ item.result.msg | default('Unknown error') }}"
          when: item.result is failed
          loop:
            - { name: "account", result: "{{ account_parse_result }}" }
            - { name: "environment", result: "{{ env_parse_result }}" }
            - { name: "group", result: "{{ group_parse_result }}" }
            - { name: "idp", result: "{{ idp_parse_result }}" }
            - { name: "service", result: "{{ service_parse_result }}" }
            - { name: "extra", result: "{{ extra_parse_result }}" }
      rescue:
        - name: Handle parsing failures
          debug:
            msg: "Critical error during variable parsing. Check deployment variables format."

        - name: Fail playbook on critical parsing errors
          fail:
            msg: "Unable to continue due to critical parsing errors."

    # Dynamic display of all variables - will adapt to any keys being added or removed
    - name: Display all account variables
      debug:
        msg: "{{ item.key }}: {{ item.value }}"
      loop: "{{ account_json | dict2items }}"
      loop_control:
        label: "account_json.{{ item.key }}"
      when: account_json is defined and account_json | length > 0

    - name: Display all environment variables
      debug:
        msg: "{{ item.key }}: {{ item.value }}"
      loop: "{{ environment_json | dict2items }}"
      loop_control:
        label: "environment_json.{{ item.key }}"
      when: environment_json is defined and environment_json | length > 0

    - name: Display all group variables
      debug:
        msg: "{{ item.key }}: {{ item.value }}"
      loop: "{{ group_json | dict2items }}"
      loop_control:
        label: "group_json.{{ item.key }}"
      when: group_json is defined and group_json | length > 0

    - name: Display all idp variables
      debug:
        msg: "{{ item.key }}: {{ item.value }}"
      loop: "{{ idp_json | dict2items }}"
      loop_control:
        label: "idp_json.{{ item.key }}"
      when: idp_json is defined and idp_json | length > 0

    - name: Display all service instance variables
      debug:
        msg: "{{ item.key }}: {{ item.value }}"
      loop: "{{ service_instance_json | dict2items }}"
      loop_control:
        label: "service_instance_json.{{ item.key }}"
      when: service_instance_json is defined and service_instance_json | length > 0

    - name: Display all extra variables
      debug:
        msg: "{{ item.key }}: {{ item.value }}"
      loop: "{{ extra_variables_json | dict2items }}"
      loop_control:
        label: "extra_variables_json.{{ item.key }}"
      when: extra_variables_json is defined and extra_variables_json | length > 0

    - name: Set facts from supplied json data
      ansible.builtin.set_fact:
        account_apikey: "{{ account_json['account_api_key'] }}"
        account_name: "{{ account_json['account_name'] }}"
        account_id: "{{ account_json['account_id'] }}"
        account_owner_id: "IBMid-662001YCY3"
        group_name: "{{ group_json['group_name'] }}"
        group_id: "{{ group_json['access_group_id'] }}"
        owner_id: "{{ environment_json['requester_id'] }}"
        cos_name: "cos-{% if '-' in environment_json['requester_id'] %}{{ (environment_json['requester_id']|split('-'))[1]|lower }}{% else %}{{ environment_json['requester_id']|lower }}{% endif %}"
        # cos_name: "CloudObjectStorage"

    - name: Show response
      ansible.builtin.debug:
        msg: "cos_name: {{ cos_name }}"

    ############################################
    # Process additional tasks using parsed variables
    ############################################
       
    - name: Example of using variables in a task
      debug:
        msg: "Creating resources for {{ environment_json.environment_id | default('unknown') }} in account {{ account_json.account_name | default('unknown') }}"
      when: environment_json is defined and account_json is defined


    # Connect using the supplied API Key and get a Bearer Token for all future
    # API calls to use.
    - name: Connect to IBM Cloud account {{ account_name }} with API key and retrieve access_token
      ansible.builtin.uri:
        url: "https://iam.cloud.ibm.com/identity/token"
        method: POST
        return_content: yes
        body_format: form-urlencoded
        body:
          {
            "apikey": "{{ account_apikey }}",
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
          }
      register: token_response
      delay: "{{ delay_seconds }}"
      retries: "{{ retry_count }}"
      when:
        - account_apikey is defined
        - account_apikey != None

    # Set the Bearer token value based on json returned by login
    - name: Set fact access_token
      ansible.builtin.set_fact:
        access_token: "{{ token_response['json'].access_token }}"
      when:
        - token_response['json'].access_token is defined                                 

# display access_token for debugging purposes
    - name: Show access_token
      ansible.builtin.debug:
        msg: "access_token: {{ access_token }}"
      when:
        - access_token is defined 

# example of IBMCLOUD CLI
    - name: Set facts for ibmcloud CLI
      ansible.builtin.set_fact:
        ibmcloud_cmd_login:  |
          export IBMCLOUD_API_KEY={{ account_apikey }}
          export CLOUD_CMD=$(which ibmcloud)
          $CLOUD_CMD login --apikey $IBMCLOUD_API_KEY -r {{ cloud_region }} {% if default_resource_group is defined %}-g {{ default_resource_group }}{% endif %}  --quiet &>/dev/null
      no_log: true
      when:
        - account_apikey is defined
        - account_apikey != None
```
## Critical Requirements

The input will contain marketing/product names (e.g., "watsonx.ai Studio", "DB2"). You MUST:

1. Search for the IBM Cloud CLI command to use the services

## Recommended Resources

- **IBM Cloud Global Catalog API**: `https://globalcatalog.cloud.ibm.com/api/v1`
  - Use to work with programmatic service names and plan names
  - Example: `https://globalcatalog.cloud.ibm.com/api/v1/{service-id}`
- **IBM Cloud Catalog**: `https://cloud.ibm.com/catalog`
  - Use to verify service exists and is active
- **IBM Cloud CLI documentation** for service creation commands
- **IBM product-specific API documentation**: https://cloud.ibm.com/docs?tab=api-docs

## Output Requirements

- Generate ONLY the Ansible Playbook by extending the Ansible Variable Headers

## Background Context

This Ansible Playbook is processed by TechZone's provisioning service to run this Playbook on top of an IBM Cloud account