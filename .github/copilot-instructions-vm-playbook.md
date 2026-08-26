# Techzone Playbook Generator

Your task is to generate an Ansible Playbook for installing and configuring software on a Redhat Linux 9.x VM

## Ansible Variable Headers
```yaml
---
################################################################################
# Playbook: install-nginx.yml
# Purpose: Install NGINX on RedHat 9.6 VM and configure default web page
# Usage: ansible-playbook install-nginx.yml -e "nginx_message='Your message here'"
################################################################################

- name: Install and Configure NGINX
  hosts: 127.0.0.1
  become: true
  gather_facts: true
  
  vars:
    # nginx_message is passed from environment override post_deploy_variables definition
    nginx_html_path: /usr/share/nginx/html/index.html
  
  tasks:
    # ------------------------------------------------------------------
    #        Input Variable processing
    # ------------------------------------------------------------------

    - name: Display loaded variables that are needed
      ansible.builtin.debug:
        msg: |
          Variables from reservation:
          nginx_message: {{ nginx_message }}

    ############################################
    # Process additional tasks using parsed variables
    ############################################
       
     - name: Update system packages
      ansible.builtin.dnf:
        name: "*"
        state: latest
        update_cache: true
      register: dnf_update
      retries: 3
      delay: 5
      until: dnf_update is succeeded
    
    - name: Install NGINX
      ansible.builtin.dnf:
        name: nginx
        state: present
      register: nginx_install
      retries: 3
      delay: 5
      until: nginx_install is succeeded
    
    - name: Create custom index.html with provided message
      ansible.builtin.copy:
        dest: "{{ nginx_html_path }}"
        content: |
          <!DOCTYPE html>
          <html lang="en">
          <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>NGINX Server</title>
              <style>
                  body {
                      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                      display: flex;
                      justify-content: center;
                      align-items: center;
                      height: 100vh;
                      margin: 0;
                      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  }
                  .container {
                      text-align: center;
                      background: white;
                      padding: 50px;
                      border-radius: 10px;
                      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                  }
                  h1 {
                      color: #333;
                      margin: 0 0 20px 0;
                  }
                  p {
                      color: #666;
                      font-size: 18px;
                      margin: 10px 0;
                  }
                  .message {
                      font-size: 24px;
                      font-weight: bold;
                      color: #667eea;
                      margin-top: 30px;
                      padding: 20px;
                      background: #f0f4ff;
                      border-radius: 5px;
                  }
              </style>
          </head>
          <body>
              <div class="container">
                  <h1>NGINX Server Running</h1>
                  <p>Welcome to your NGINX web server</p>
                  <div class="message">
                      {{ nginx_message }}
                  </div>
                  <p style="margin-top: 30px; color: #999; font-size: 14px;">
                      Hostname: <code>{{ ansible_hostname }}</code>
                  </p>
              </div>
          </body>
          </html>
        owner: root
        group: root
        mode: '0644'
      notify: Restart NGINX
    
    - name: Enable NGINX service
      ansible.builtin.systemd:
        name: nginx
        enabled: true
    
    - name: Start NGINX service
      ansible.builtin.systemd:
        name: nginx
        state: started
      register: nginx_service
    
    - name: Verify NGINX is running
      ansible.builtin.systemd:
        name: nginx
      register: nginx_status
      failed_when: nginx_status.status.ActiveState != "active"
    
    - name: Display success message
      ansible.builtin.debug:
        msg:
          - "✓ NGINX successfully installed and started"
          - "✓ Message configured: '{{ nginx_message }}'"
          - "✓ NGINX is running on http://{{ ansible_default_ipv4.address }}"
          - "✓ Hostname: {{ ansible_hostname }}"
  
    # ------------------------------------------------------------------
    #        Example of Generating Post-Deploy Output
    # ------------------------------------------------------------------
    - name: Create post-deploy HTML output file
      ansible.builtin.copy:
        dest: ../post_deploy_text_output.txt
        content: |
          <style>
          .additionalInstructions {
            font-family: Arial, sans-serif;
            margin: 20px;
          }
          .additionalInstructions h4 {
            font-size: 1.2em;
            font-weight: normal;
            background-color: #002d9c;
            border: 1px solid #b6dfc5;
            padding: 10px;
            border-radius: 5px;
            color: #dde1e6;
          }
          .additionalInstructions .bold {
            font-weight: bold;
            color: #ffffff;
          }
          .additionalInstructions table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
          }
          .additionalInstructions td {
            border: 1px solid #cce3d0;
            padding: 12px;
            font-size: 0.95em;
            background-color: #d0e2ff;
          }
          .additionalInstructions tr:nth-child(even) td {
            background-color: #f1f9f4;
          }
          .additionalInstructions code, pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow-x: hidden;
            display: block;
            background-color: #f4f4f4;
            padding: 10px;
          }
          </style>
          <div class="additionalInstructions" id="additionalInstructions">
            <h4><span class="bold">**Techzone Samples**</span></h4>
            <table>
              <tbody>
                <tr>
                  <td colspan="100%">
                    <div>
                      <h2>Configuration Output</h2>
                      <ul>
                        <li> 
                        - "✓ NGINX successfully installed and started"
                        - "✓ Message configured: '{{ nginx_message }}'"
                        - "✓ NGINX is running on http://{{ ansible_default_ipv4.address }}"
                        - "✓ Hostname: {{ ansible_hostname }}" 
                        </li>
                      </ul>
                    </td>
                </tr>
              </tbody>
            </table>
          </div>
        mode: '0644'

  handlers:
    - name: Restart NGINX
      ansible.builtin.systemd:
        name: nginx
        state: restarted
```

## Critical Requirements

1. When receiving variables in the playbook, do not code them as:
```db2_version: "{{ db2_version | default('11.5.9.0') }}"```
but rather specify them with hard code default values like this:
```db2_version: "11.5.9.0"```

2. The input will contain marketing/product names (e.g., "watsonx.ai Studio", "DB2"). You MUST:

Search for the IBM Cloud CLI command to use the services

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

This Ansible Playbook is processed by TechZone's provisioning service to run this Playbook inside an Redhat 9.x VM during the Cloud-Init phase of provsioning