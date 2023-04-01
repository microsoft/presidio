# Script to download the required packages to run Presidio on Synapse,
# particularly when a workspace is Data Exfiltration Protection (DEP) enabled 
# which will not allow Synapse to connect to external data sources or common Python public repositories like Python Package Index (PyPI).
# This script must be run in an Ubuntu 18.04+ environment with network connectivity to the workspace. 
# For windows users, the easiest method is to install the Ubuntu terminal environment app through the Microsoft Store, # otherwise utilise an Ubuntu VM in Azure

# Declarations
declare SynapseWorkspaceName="YOURWORKSPACENAME"
declare TenantId="TENANTID"
declare SubscriptionId="SUBSCRIPTIONID"

sudo apt-get install python3-setuptools
sudo apt-get update
sudo apt-get install python3-pip
mkdir presidiodeps
cd presidiodeps
echo -e "presidio_analyzer\npresidio_anonymizer\nnumpy==1.23.4" > requirements.txt
pip3 wheel -r requirements.txt

# Install Powershell and Azure PowerShell cmdlet for Azure Synapse Analytics
sudo apt-get install -y wget apt-transport-https software-properties-common
wget -q https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y powershell

# Install pwsh modules for Synapse and Accounts
pwsh -Command Install-Module -Name Az.Accounts
pwsh -Command Install-Module -Name Az.Synapse

# Add a line to the powershell script to connect to your Azure subscription using device flow
echo "Connect-AzAccount -UseDeviceAuthentication -TenantId $TenantId -SubscriptionId $SubscriptionId" > upload.ps1

# Generate the list of packages to upload
for i in *.whl; do echo "New-AzSynapseWorkspacePackage -WorkspaceName $SynapseWorkspaceName -Package $i"; done >> upload.ps1

# Download the language pack. Note this may take some time
wget -q https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.4.0/en_core_web_lg-3.4.0-py3-none-any.whl
# Add another entry for the desired language model. This could also be invoked by running python -m spacy download en_core_web_lg
echo "New-AzSynapseWorkspacePackage -WorkspaceName $SynapseWorkspaceName -Package en_core_web_lg-3.4.0-py3-none-any.whl" >> upload.ps1

# Run the upload, note that you will be prompted to connect and authenticate to your subscription using devicelogin url and code. The upload process may take some time.
pwsh upload.ps1
