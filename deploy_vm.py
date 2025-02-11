# Script Overview:
# This script automates the provisioning of a VM instance in Google Cloud Platform (GCP) using the Compute Engine API.
# The script handles three main components in sequence:
# 1. Static IP Allocation: Reserves a static external IP address for consistent network addressing
# 2. Network Security: Configures firewall rules for SSH and HTTP access
# 3. VM Instance Creation: Provisions a compute instance with specified resources and configurations

# Required Dependencies:
# time: Provides delay functionality for API rate limiting and operation polling
import time
# googleapiclient.discovery: GCP API client library for making authenticated API requests
# Handles REST API interactions, request formatting, and response parsing
from googleapiclient import discovery

def wait_for_operation(compute, project, zone, operation):
    # Polls a zone-specific operation until completion
    # Required because GCP operations are asynchronous and need to be monitored
    # Parameters are validated by the compute API client
    print("Waiting for operation to finish")
    while True:
        # Query operation status using zoneOperations API endpoint
        # Returns operation object containing current status and potential error details
        result = compute.zoneOperations().get(project=project,zone=zone, operation = operation).execute()
        if result.get('status') =='DONE':
            # Check for operation errors and propagate them if present
            if 'error' in result:
                raise Exception(result['error'])
            break
        # API rate limits
        time.sleep(1)

def wait_for_global_operation(compute,project,operation):
    # Polls a global operation until completion
    # Global operations affect project-wide resources like firewall rules
    # Uses globalOperations API endpoint instead of zoneOperations
    print("waiting for a global operation to finish")
    while True:
        result = compute.globalOperations().get(project=project,operation=operation).execute()
        if result.get('status') == 'DONE':
            if 'error' in result:
                raise Exception(result['error'])
            break
        time.sleep(1)

def create_address(compute,project,region,address_name):
    # Allocates a static external IP address in the specified region
    # Static IPs provide consistent network addressing for instances
    # Critical for DNS configuration and external service reliability
    
    # Initialize address creation operation through the addresses API
    operation = compute.addresses().insert(
        project=project,
        region=region,
        body={'name':address_name}
    ).execute()

    # Monitor the address allocation operation
    # Region operations are distinct from zone and global operations
    while True:
        result = compute.regionOperations().get(
            project=project, region=region, operation=operation['name']
        ).execute()
        if result.get('status') == 'DONE':
            break
        time.sleep(1)

    # Retrieve the allocated IP address details
    # Returns the address object containing the actual IP address
    address = compute.addresses().get(
        project=project, region=region, address=address_name
    ).execute()
    return address['address']

def create_firewall_rule(compute,project, firewall_name):
    # Configures ingress firewall rules for the VPC network
    # Defines allowed inbound traffic patterns based on protocol and port
    print(f"Creating firewall rule '{firewall_name}' ")
    
    # Define firewall rule configuration
    # Specifies protocols, ports, and source IP ranges
    firewall_body = {
        'name': firewall_name,
        'allowed': [
            # TCP protocol rules for SSH (22) and HTTP (80)
            # Required for remote access and web server functionality
            {'IPProtocol':'tcp', 'ports':['22','80']}
        ],
        'direction':'INGRESS',  # Applies to incoming traffic only
        'sourceRanges': ['0.0.0.0/0']  # Allows traffic from all IPv4 addresses (production environments should restrict this)
    }
    # Create firewall rule through the firewalls API endpoint
    operation = compute.firewalls().insert(project=project,body=firewall_body).execute()
    wait_for_global_operation(compute, project, operation['name'])
    print("Firewall rule created.")

def create_instance(compute,project,zone,instance_name,static_ip,machine_type,source_image,disk_size_gb):
    # Provisions a new Compute Engine instance with specified configurations
    # Handles instance metadata, networking, and storage configurations
    print(f"Creating VM instance '{instance_name}' in zone '{zone}'")
    
    # Construct the full machine type URI required by the API
    # Combines zone and machine type into the expected format
    machine_type_full = f"zones/{zone}/machineTypes/{machine_type}"

    # Define the complete instance configuration
    # Specifies all required instance properties and resources
    config = {
        'name':instance_name,  # Instance identifier within project
        'machine_type':machine_type_full,  # Hardware configuration (CPU/memory)
        'disks': [{
            'boot': True,  # Designates as boot disk
            'autoDelete':True,  # Disk is deleted with instance deletion
            'initializeParams':{
                'sourceImage':source_image,  # Base OS image for boot disk
                'diskSizeGb':disk_size_gb   # Boot disk capacity in GB
            }
        }],
        'networkInterfaces': [{
            'network': 'global/networks/default',  # VPC network configuration
            'accessConfigs':[{
                'name': 'External_NAT',
                'type': 'ONE_TO_ONE_NAT',  # Enables internet connectivity
                'natIP':static_ip  # Associates the reserved static IP
            }]
        }],
        'tags':{
            'items':['http-server','ssh-server']  # Network tags for firewall rule association
        }
    }
    
    # Initialize instance creation through instances API endpoint
    operation = compute.instances().insert(
        project=project,
        zone=zone,
        body=config
    ).execute()
    wait_for_operation(compute,project,zone,operation['name'])
    print('VM INSTANCE CREATED SUCCESSFULLY!')

def main():
    # Primary execution function
    # Defines configuration parameters and orchestrates resource creation
    
    project = 'cloud-assignment-450118'  # GCP project identifier
    region = 'us-central1'               # Regional location for resource deployment
    zone = 'us-central1-a'              # Specific availability zone within region

    # Resource identifiers for created components
    address_name = 'vm-static-ip'
    firewall_name = 'allow-ssh-http'
    instance_name = 'cloud-ca-vm-instance'

    # Instance specifications
    machine_type = 'n1-standard-2'  # n1-standard-2 provides 2 vCPUs and 7.5GB RAM
    disk_size_gb = 250             # Boot disk capacity in GB

    # Base OS image specification
    # Ubuntu 20.04 LTS from the public images project
    source_image = "projects/ubuntu-os-cloud/global/images/family/ubuntu-2004-lts"

    # Initialize the Compute Engine API client
    compute = discovery.build('compute','v1')

    # Execute resource creation in dependency order:
    
    # 1. Allocate static IP address
    # Required before instance creation for IP assignment
    static_ip = create_address(compute,project,region,address_name)
    print(f"reserved static IP: {static_ip}")

    # 2. Configure firewall rules
    # Establishes network security before instance becomes active
    create_firewall_rule(compute,project,firewall_name)

    # 3. Create and configure the VM instance
    create_instance(compute,project,zone,instance_name,static_ip,machine_type,source_image,disk_size_gb)

# Standard Python idiom for script execution
# Ensures main() only runs if script is executed directly
if __name__ == '__main__':
    main()
