# Instructions for Generating a VPC Multi-VM Manifest

## Coding Standards

- **Language:** Prioritize YAML for implementation (JSON also supported).
- **Formatting:** Adhere to proper YAML indentation (2 spaces per level).
- **Naming Conventions:** Use kebab-case for VM names, snake_case for configuration keys.
- **Comments:** Use YAML comments (#) to document complex configurations.
- **Validation:** Ensure all required fields are present and values match allowed types.
- **Version Control:** Store manifests in version control with descriptive commit messages.
- **Documentation:** Document any custom configurations or deviations from defaults.
- **Security:** Never hardcode secrets; use secret management for sensitive data.
- **Testing:** Test manifests incrementally, starting with minimal configuration.
- **Best Practices:** Follow IBM Cloud VPC naming conventions and resource limits.

# VPC Multi-VM Manifest Generator

Your task is to generate a YAML manifest for deploying multiple virtual machines in IBM Cloud VPC infrastructure. The manifest defines VPC infrastructure (shared or create mode), VM configurations, networking, storage, and optional post-deployment automation.

## User Input Requirements

**CRITICAL: When generating manifests with post-deploy automation, you MUST ask the user for:**

1. **Repository Name**: The repository name from the ITZ Content organization (e.g., `my-custom-repo`)
   - This will be used to construct both the repository URL and secrets path
   - Repository URL format: `git@github.ibm.com:itz-content/{repository-name}.git`
   - Secrets path format: `techzone/itz/provisioning-secrets/itz-content/{repository-name}`

**Why this is required:**
- The VPC manifest pattern requires deploy keys to be stored in TechZone secrets manager
- Deploy keys **CANNOT** be set directly in the manifest or as variables
- This is a unique requirement for this pattern compared to other TechZone patterns
- The secrets path uses the same repository name, so only one input is needed

**Example prompt to user:**
```
To configure post-deploy automation, I need your repository name from the ITZ Content organization.
Example: If your repo is git@github.ibm.com:itz-content/my-custom-repo.git, provide: my-custom-repo

Please provide your repository name:
```

**How to construct the values:**
- Repository URL: `git@github.ibm.com:itz-content/{repository-name}.git`
- Secrets path: `techzone/itz/provisioning-secrets/itz-content/{repository-name}`

## Rules and Standards

### Manifest Structure

The manifest must contain three main sections:

1. **version** (required): Must be `"1.0"`
2. **vpc** (required): Contains infrastructure and VM definitions
3. **post_deploy** (optional): Pattern-level post-deployment orchestration

### VPC Section Structure

```yaml
vpc:
  version: "1.0"
  infrastructure:
    mode: shared  # or "create"
    # ... infrastructure config
  vms:
    - name: vm-name
      # ... VM config
```

### Infrastructure Modes

**SHARED Mode (Recommended):**
- Uses existing VPC infrastructure
- Automatically discovers VPC using `vpc_name_prefix` (default: `itz-vpc-`)
- No VPC creation or management required
- Suitable for most use cases

**CREATE Mode:**
- Creates new VPC infrastructure
- Requires `vpc_name` field
- Creates subnets, security groups, and gateways
- Use for isolated environments

### VM Configuration Requirements

Each VM must have:
- `name` (required): Unique VM identifier
- `image_name` (required): IBM Cloud stock image name
- `os_type` (required): One of: `rhel`, `sles`, `ubuntu`, `windows`, `zos`
- `profile_name` (required): IBM Cloud compute profile (e.g., `bx2-4x16`)

### Operating System Standards

**Linux VMs (RHEL, SLES, Ubuntu):**
- Default SSH port: `2223`
- Support cloud-init and SSH post-deploy modes
- Can enable VNC, noVNC, Cockpit
- Support patching, hardening, FQDN configuration

**Windows VMs:**
- Default RDP port: `51124`
- Default WinRM port: `5986`
- Support cloud-init post-deploy mode only
- Can enable secure WinRM
- Support patching, hardening, FQDN configuration

### Image Name Examples

**RHEL:**
- `ibm-redhat-9-6-minimal-amd64`
- `ibm-redhat-9-4-minimal-amd64`
- `ibm-redhat-8-10-minimal-amd64`

**SLES:**
- `ibm-sles-15-6-amd64`
- `ibm-sles-12-5-amd64`

**Ubuntu:**
- `ibm-ubuntu-24-04-minimal-amd64`
- `ibm-ubuntu-22-04-minimal-amd64`

**Windows:**
- `ibm-windows-server-2022-full-standard-amd64`
- `ibm-windows-server-2025-full-standard-amd64`

### Compute Profile Examples

Format: `{family}{generation}-{vCPUs}x{RAM_GB}`

**Balanced (bx2):** General-purpose workloads
- `bx2-2x8`, `bx2-4x16`, `bx2-8x32`, `bx2-16x64`

**Compute (cx2):** Compute-intensive workloads
- `cx2-2x4`, `cx2-4x8`, `cx2-8x16`

**Memory (mx2):** Memory-intensive workloads
- `mx2-2x16`, `mx2-4x32`, `mx2-8x64`

### Security Group Configuration

**Default Ports:**
- SSH: `2223` (Linux/z/OS)
- HTTPS: `443`
- RDP: `51124` (Windows)
- WinRM: `5986` (Windows, if secure WinRM enabled)
- VNC: `5901` (Linux, if VNC enabled)

**Port Configuration:**
```yaml
security_group:
  public_tcp_ports: [22, 443, 8080]  # Additional public TCP ports
  public_udp_ports: []                # Additional public UDP ports
```

### Post-Deploy Modes

**Per-VM Post-Deploy (cloud-init or ssh):**
- Runs on individual VMs during or after provisioning
- Supports scripts and Ansible playbooks
- Can clone Git repositories
- Supports secret management and COS file downloads

**Pattern-Level Post-Deploy (container):**
- Runs after all VMs are provisioned
- Executes in container environment
- Can orchestrate across multiple VMs
- Has access to all VM details (IPs, FQDNs, names)
- Supports Git repositories, secrets, and COS files

### Post-Deploy Structure

**IMPORTANT: Secret Management for Post-Deploy**

A critical requirement unique to the VPC manifest pattern is that GitHub deploy keys **MUST** be stored in the TechZone secrets manager. Unlike other patterns, deploy keys cannot be set directly within the manifest or as a `post_deploy_deploy_key` variable.

**When generating manifests with post-deploy automation:**
1. **Ask the user** for their repository name (e.g., `my-custom-repo`)
2. **Construct the repository URL**: `git@github.ibm.com:itz-content/{repository-name}.git`
3. **Construct the secrets path**: `techzone/itz/provisioning-secrets/itz-content/{repository-name}`
4. The deploy key must be stored at this path with the key name `deploy_key`

**Example with repository name `my-custom-repo`:**
```yaml
repository: "git@github.ibm.com:itz-content/my-custom-repo.git"

secret_groups:
  - type: keymaster
    path: "techzone/itz/provisioning-secrets/itz-content/my-custom-repo"
    keys: ["deploy_key"]
```

**Per-VM (cloud-init mode):**
```yaml
post_deploy:
  mode: cloud-init
  version: "1.0"
  
  config:
    work_dir: "/root/post_deploy_jobs"
    cleanup: true
  
  jobs:
    - name: job-name
      description: "Job description"
      repository: "git@github.ibm.com:itz-content/REPO_NAME.git"  # Ask user for repository name, then construct URL
      branch: "main"
      
      # REQUIRED: Deploy key must be in TechZone secrets manager
      # Secrets path uses same repository name
      secret_groups:
        - type: keymaster
          path: "techzone/itz/provisioning-secrets/itz-content/REPO_NAME"  # Use same repository name
          keys: ["deploy_key"]
      
      tasks:
        - name: task-name
          script: "scripts/setup.sh"
          variables:
            key: "value"
```

**Pattern-Level (container mode):**
```yaml
post_deploy:
  mode: container
  version: "1.0"
  
  jobs:
    - name: orchestration-job
      repository: "git@github.ibm.com:itz-content/REPO_NAME.git"  # Ask user for repository name, then construct URL
      
      # REQUIRED: Deploy key must be in TechZone secrets manager
      # Secrets path uses same repository name
      secret_groups:
        - type: keymaster
          path: "techzone/itz/provisioning-secrets/itz-content/REPO_NAME"  # Use same repository name
          keys: ["deploy_key"]
      
      tasks:
        - name: configure-landscape
          script: "orchestrate.sh"
```

## Recommended Resources

- **IBM Cloud VPC Documentation**: `https://cloud.ibm.com/docs/vpc`
- **IBM Cloud Stock Images**: `https://cloud.ibm.com/docs/vpc?topic=vpc-about-images`
- **IBM Cloud Instance Profiles**: `https://cloud.ibm.com/docs/vpc?topic=vpc-profiles`
- **VPC Manifest Specification**: See `design/V1_VPC_MANIFEST.md`
- **Example Manifests**: See `examples/` directory

## Output Requirements

- Generate ONLY the YAML manifest with applied values
- Do NOT create Terraform code
- Maintain proper YAML structure with correct indentation
- All string values should use double quotes for consistency
- Boolean values should be lowercase (`true`/`false`)
- Include comments for complex configurations
- Validate against the manifest specification
- **If post-deploy is included**: Use placeholder `REPO_NAME` and ask the user for their repository name to construct both the repository URL and secrets path

## Background Context

This YAML manifest is processed by TechZone's provisioning service using Terraform. The manifest is parsed and used to:
1. Discover or create VPC infrastructure
2. Provision virtual machines with specified configurations
3. Configure networking, storage, and security
4. Execute post-deployment automation

A single incorrect value or malformed YAML will cause the entire provisioning to fail.

---

## Example Outputs

### Example 1: Simple Two-VM Deployment (RHEL + Windows)

```yaml
version: "1.0"

vpc:
  version: "1.0"
  
  infrastructure:
    mode: shared
    vpc_name_prefix: itz-vpc-
    
    subnets:
      0:
        count: 1
        enable_public_gateway: true
    
    security_group:
      public_tcp_ports: [2223, 443, 51124, 5986]
      public_udp_ports: []
  
  vms:
    - name: rhel-server
      image_name: ibm-redhat-9-6-minimal-amd64
      os_type: rhel
      profile_name: bx2-4x16
      
      boot_volume_size: 100
      boot_volume_profile: general-purpose
      
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
    
    - name: windows-server
      image_name: ibm-windows-server-2022-full-standard-amd64
      os_type: windows
      profile_name: bx2-4x16
      
      boot_volume_size: 100
      boot_volume_profile: general-purpose
      
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_secure_winrm: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
```

### Example 2: Multi-VM with Per-VM Post-Deploy

```yaml
version: "1.0"

vpc:
  version: "1.0"
  
  infrastructure:
    mode: shared
    vpc_name_prefix: itz-vpc-
    
    subnets:
      0:
        count: 1
        enable_public_gateway: true
    
    security_group:
      public_tcp_ports: [2223, 443, 8080]
      public_udp_ports: []
  
  vms:
    - name: web-server
      image_name: ibm-redhat-9-6-minimal-amd64
      os_type: rhel
      profile_name: bx2-4x16
      
      boot_volume_size: 100
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
      
      post_deploy:
        mode: cloud-init
        version: "1.0"
        
        jobs:
          - name: install-apache
            description: "Install and configure Apache web server"
            # USER INPUT REQUIRED: Ask user for repository name (e.g., web-config)
            repository: "git@github.ibm.com:itz-content/REPO_NAME.git"
            branch: "main"
            
            # Deploy key must be stored in TechZone secrets manager
            # Secrets path uses same repository name
            secret_groups:
              - type: keymaster
                path: "techzone/itz/provisioning-secrets/itz-content/REPO_NAME"
                keys: ["deploy_key"]
            
            tasks:
              - name: setup-apache
                script: "scripts/install-apache.sh"
                variables:
                  server_name: "web-server"
                  port: "8080"
    
    - name: app-server
      image_name: ibm-redhat-9-6-minimal-amd64
      os_type: rhel
      profile_name: bx2-8x32
      
      boot_volume_size: 150
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
      
      post_deploy:
        mode: cloud-init
        version: "1.0"
        
        jobs:
          - name: install-nodejs
            description: "Install Node.js application"
            # USER INPUT REQUIRED: Ask user for repository name (e.g., app-config)
            repository: "git@github.ibm.com:itz-content/REPO_NAME.git"
            branch: "main"
            
            # Deploy key must be stored in TechZone secrets manager
            # Secrets path uses same repository name
            secret_groups:
              - type: keymaster
                path: "techzone/itz/provisioning-secrets/itz-content/REPO_NAME"
                keys: ["deploy_key"]
            
            tasks:
              - name: setup-nodejs
                playbook: "playbooks/install-nodejs.yaml"
                variables:
                  node_version: "18"
```

### Example 3: Multi-VM with Pattern-Level Orchestration

```yaml
version: "1.0"

post_deploy_config:
  primary_text_source: "combined"
  primary_json_source: "combined"
  inject_vm_outputs: true

vpc:
  version: "1.0"
  
  infrastructure:
    mode: shared
    vpc_name_prefix: itz-vpc-
    
    subnets:
      0:
        count: 1
        enable_public_gateway: true
    
    security_group:
      public_tcp_ports: [2223, 443, 8080, 5432]
      public_udp_ports: []
  
  vms:
    - name: web-server-1
      image_name: ibm-redhat-9-6-minimal-amd64
      os_type: rhel
      profile_name: bx2-4x16
      
      boot_volume_size: 100
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
    
    - name: web-server-2
      image_name: ibm-redhat-9-6-minimal-amd64
      os_type: rhel
      profile_name: bx2-4x16
      
      boot_volume_size: 100
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
    
    - name: database-server
      image_name: ibm-redhat-9-6-minimal-amd64
      os_type: rhel
      profile_name: bx2-8x32
      
      boot_volume_size: 200
      enable_public_ip: false
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true

post_deploy:
  mode: container
  version: "1.0"
  
  jobs:
    - name: configure-cluster
      description: "Configure web cluster with load balancing"
      # USER INPUT REQUIRED: Ask user for repository name (e.g., cluster-orchestration)
      repository: "git@github.ibm.com:itz-content/REPO_NAME.git"
      branch: "main"
      
      # Deploy key must be stored in TechZone secrets manager
      # Secrets path uses same repository name
      secret_groups:
        - type: keymaster
          path: "techzone/itz/provisioning-secrets/itz-content/REPO_NAME"
          keys: ["deploy_key"]
      
      tasks:
        - name: setup-load-balancer
          script: "scripts/configure-lb.sh"
          variables:
            backend_servers: "web-server-1,web-server-2"
            database_server: "database-server"
        
        - name: validate-cluster
          script: "scripts/validate-cluster.sh"
          variables:
            check_type: "full"
```

### Example 4: Five-VM Multi-OS Deployment

```yaml
version: "1.0"

vpc:
  version: "1.0"
  
  infrastructure:
    mode: shared
    vpc_name_prefix: itz-vpc-
    
    subnets:
      0:
        count: 1
        enable_public_gateway: true
    
    security_group:
      public_tcp_ports: [2223, 443, 51124, 5986]
      public_udp_ports: []
  
  vms:
    - name: rhel-vm
      image_name: ibm-redhat-9-6-minimal-amd64
      os_type: rhel
      profile_name: bx2-4x16
      boot_volume_size: 100
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
    
    - name: sles-vm
      image_name: ibm-sles-15-6-amd64
      os_type: sles
      profile_name: bx2-4x16
      boot_volume_size: 120
      boot_volume_profile: 5iops-tier
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
    
    - name: ubuntu-vm
      image_name: ibm-ubuntu-24-04-minimal-amd64
      os_type: ubuntu
      profile_name: bx2-4x16
      boot_volume_size: 100
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
    
    - name: windows-2022-vm
      image_name: ibm-windows-server-2022-full-standard-amd64
      os_type: windows
      profile_name: bx2-4x16
      boot_volume_size: 100
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_secure_winrm: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
    
    - name: windows-2025-vm
      image_name: ibm-windows-server-2025-full-standard-amd64
      os_type: windows
      profile_name: bx2-4x16
      boot_volume_size: 100
      boot_volume_profile: 10iops-tier
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_secure_winrm: true
        enable_patching: true
        enable_hardening: true
        enable_reboot: true
```

## Common Configuration Patterns

### Minimal Configuration (Single VM)

```yaml
version: "1.0"

vpc:
  version: "1.0"
  
  infrastructure:
    mode: shared
    vpc_name_prefix: itz-vpc-
    
    subnets:
      0:
        count: 1
        enable_public_gateway: true
    
    security_group:
      public_tcp_ports: [2223, 443]
      public_udp_ports: []
  
  vms:
    - name: simple-vm
      image_name: ibm-redhat-9-6-minimal-amd64
      os_type: rhel
      profile_name: bx2-2x8
      
      enable_public_ip: true
      primary_subnet_number: 1
      
      dns:
        enabled: true
        ttl: 900
      
      config:
        enable_postinstall: true
        enable_fqdn: true
        enable_patching: true
        enable_reboot: true
```

### High-Performance Configuration

```yaml
- name: high-perf-vm
  image_name: ibm-redhat-9-6-minimal-amd64
  os_type: rhel
  profile_name: bx2-16x64  # High CPU and memory
  
  boot_volume_size: 250
  boot_volume_profile: 10iops-tier  # High IOPS storage
  
  additional_volumes:
    data1:
      size: 1000
      profile: 10iops-tier
  
  enable_public_ip: true
  primary_subnet_number: 1
  
  dns:
    enabled: true
    ttl: 900
  
  config:
    enable_postinstall: true
    enable_fqdn: true
    enable_patching: true
    enable_hardening: true
    enable_reboot: true
```

### Private VM Configuration (No Public IP)

```yaml
- name: private-vm
  image_name: ibm-redhat-9-6-minimal-amd64
  os_type: rhel
  profile_name: bx2-4x16
  
  boot_volume_size: 100
  enable_public_ip: false  # No public IP
  primary_subnet_number: 1
  
  dns:
    enabled: false  # DNS requires public IP
  
  config:
    enable_postinstall: true
    enable_fqdn: true
    enable_patching: true
    enable_hardening: true
    enable_reboot: true
  
  post_deploy:
    mode: cloud-init  # Use cloud-init for private VMs
    version: "1.0"
    # ... post-deploy configuration
```

## Best Practices

1. **Start Simple**: Begin with minimal configuration and add complexity incrementally
2. **Test Incrementally**: Test per-VM configuration before adding pattern-level orchestration
3. **Use Shared Mode**: Prefer shared VPC mode unless you need isolated infrastructure
4. **Right-Size Resources**: Choose appropriate compute profiles and storage for your workload
5. **Security First**: Enable hardening and patching for production deployments
6. **Document Changes**: Use YAML comments to document custom configurations
7. **Version Control**: Store manifests in Git with descriptive commit messages
8. **Secret Management**: Always use secret_groups for sensitive data, never hardcode
9. **DNS Configuration**: Enable DNS for VMs that need discoverable hostnames
10. **Post-Deploy Testing**: Use `post_deploy_display_jobs: true` during development

## Validation Checklist

Before deploying your manifest, verify:

- [ ] Manifest version is `"1.0"`
- [ ] VPC section has `version: "1.0"`
- [ ] Infrastructure mode is either `shared` or `create`
- [ ] All VMs have required fields: name, image_name, os_type, profile_name
- [ ] Image names match available IBM Cloud stock images
- [ ] OS types match the selected images
- [ ] Compute profiles are valid IBM Cloud profiles
- [ ] Security group ports include all required access ports
- [ ] DNS is only enabled for VMs with public IPs
- [ ] Post-deploy repositories exist and deploy keys are configured
- [ ] Secret paths are correct in secret_groups
- [ ] YAML syntax is valid (proper indentation, no tabs)

## Troubleshooting

**Common Issues:**

1. **Invalid YAML syntax**: Use a YAML validator to check indentation
2. **Missing required fields**: Ensure all required VM fields are present
3. **Invalid image name**: Verify image exists in IBM Cloud catalog
4. **OS type mismatch**: Ensure os_type matches the image operating system
5. **Invalid profile**: Check that compute profile exists in target region
6. **DNS without public IP**: DNS requires enable_public_ip: true
7. **Post-deploy failures**: Check repository access and deploy key configuration
8. **Port conflicts**: Ensure security group includes all required ports

## Additional Resources
- [IBM Cloud VPC Documentation](https://cloud.ibm.com/docs/vpc)
- [TechZone Support](https://techzone.ibm.com/support)