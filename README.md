# Google Cloud VM Deployment Script

This repository contains a Python script that automates the deployment of a Google Cloud Compute Engine VM instance. The script performs the following tasks:

- Reserves a static external IP address.
- Creates a firewall rule to allow SSH (port 22) and HTTP (port 80) access.
- Deploys a VM instance using Ubuntu 20.04 with at least 2 vCPUs, 8GB RAM, and a 250GB boot disk.

The repository also includes instructions for verifying the deployment via the Google Cloud Console, SSH access, and HTTP access (by hosting a simple "Hello World" webpage using Apache).

---


## Prerequisites

1. **Google Cloud SDK (gcloud):**  
   Install the Google Cloud SDK on your local machine. Follow the guide here:  
   [Installing Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

2. **Authentication:**  
   - Log in to your account using:
     ```bash
     gcloud auth login
     ```
   - Set up Application Default Credentials (required for API access in the script):
     ```bash
     gcloud auth application-default login
     ```

3. **Google Cloud Project and APIs:**  
   - Create or use an existing project in the [Google Cloud Console](https://console.cloud.google.com/).
   - Set your project as the default:
     ```bash
     gcloud config set project cloud-assignment-450118
     ```
   - Enable the necessary APIs:
     ```bash
     gcloud services enable compute.googleapis.com iam.googleapis.com
     ```

4. **Python 3 and Required Packages:**  
   Ensure Python 3 is installed, then install the required package:
   ```bash
   pip install google-api-python-client

## Google Cloud project setup
- Create a new Google Cloud project or use an existing one.
- Set your project as the default:
  ```bash
gcloud config set project PROJECT_ID
``

- It can be easier to do this step in the Cloud Console.

- Enbable the APIs we need for this project:
```bash
gcloud services enable compute.googleapis.com iam.googleapis.com
````

## Python 3 and Required Packages.
Ensure Python is installed. Then install the required package:
```bash
pip3 install google-api-python-client
````
- If you encounter an error saying "Module not found" make sure to install the python module in the correct path in AppData/Program/Python/Python3xx/lib.

## Set up and Configuration
1. Clone the repository.
```bash
git clone https://github.com/SipByMeDev/deploy-vm-google-cloud.git
cd deploy-vm-google-cloud
````
2. Configure the Script
-Open the script and in your preferred editor update the variables for your requirements.

## Running the Script.
1. Ensure to navigate to the repository directory.
2. Run the script.
```` bash
python3 deploy_vm.py
````

## Verification.
1. Verify the VM is running.
- Using Google Cloud Console you can check the Compute Engine dashboard.
- Using the gcloud CLI.
````bash
gcloud compute instances list
````
-Status column should indicate RUNNING

## SSH Access to the VM
- Using the gcloud Command.
```bash
gcloud compute cloud-ca-vm-instance --zone=us-central1-a
````
## HTTP Access hosting a "hello world" webpage
1. SSH into the VM as above.
2. Install Apache web server.
````bash
sudo apt update
sudo apt install apache2 -y
````
3. Edit the default web page using Nano:
```bash
sudo nano /var/www/html/index.html
````
- Replace the contents with:
```html
<html>
  <head>
    <title>Hello world</title>
  </head>
  <body>
    <h1>Hello World</h1>
  </body>
</html>
````
- There will be keyboard shortcuts displayed on the bottom, you  may use yo edit the index.html.
- View the webpage:
```bash
gcloud compute instances list
````
-Find the VM's external IP address and put into your browser to fetch the page.

## Troubleshooting.
Common issues and resolutions:
- Missing default credentials:
- If you encounter authentication errors, run:
```bash
gcloud auth application-default login
````
- Instance not running:
- check the status using 
```bash
gcloud compute instances list
````
-HTTP Access Issues:
-Ensure Apache is installed and running
```bash
sudo systemctl status apache2
````
- Confirm that the firewall rule is correctly configured to allow HTTP traffic, port 80.








