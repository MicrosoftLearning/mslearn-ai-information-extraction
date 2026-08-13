#!/bin/bash
# Task 4 - upload the Fabrikam Logistics sample forms used to train a custom
# Document Intelligence extraction model.
#
# This creates a storage account, uploads the labeled training forms, and
# prints a Shared Access Signature (SAS) URI you paste into Document
# Intelligence Studio.
#
# The training forms are the ones that already ship with this repo, so nothing
# is duplicated. Override SAMPLE_FORMS_DIR if you keep them somewhere else.

# Set variable values
subscription_id="YOUR_SUBSCRIPTION_ID"
resource_group="YOUR_RESOURCE_GROUP"
location="YOUR_LOCATION_NAME"
expiry_date="2028-01-01T00:00:00Z"

# Labeled training forms shipped with the repo (relative to this script).
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLE_FORMS_DIR="${SAMPLE_FORMS_DIR:-$script_dir/../../03-document-intelligence/custom/sample-forms}"

if [ ! -d "$SAMPLE_FORMS_DIR" ]; then
    echo "Could not find the sample forms at: $SAMPLE_FORMS_DIR"
    echo "Set SAMPLE_FORMS_DIR to the folder that holds the labeled training forms."
    exit 1
fi

# Get random numbers to create unique resource names
unique_id=$((1 + RANDOM % 99999))

# Create a storage account in your Azure resource group
echo "Creating storage..."
az storage account create --name "fabrikamform$unique_id" --subscription "$subscription_id" --resource-group "$resource_group" --location "$location" --sku Standard_LRS --encryption-services blob --default-action Allow --allow-blob-public-access true --only-show-errors --output none

echo "Uploading files from $SAMPLE_FORMS_DIR ..."
# Get storage key to create a container in the storage account
key_json=$(az storage account keys list --subscription "$subscription_id" --resource-group "$resource_group" --account-name "fabrikamform$unique_id" --query "[?keyName=='key1'].{keyName:keyName, permissions:permissions, value:value}")
key_string=$(echo "$key_json" | jq -r '.[0].value')
AZURE_STORAGE_KEY=${key_string}

# Create a container
az storage container create --account-name "fabrikamform$unique_id" --name sampleforms --public-access blob --auth-mode key --account-key "$AZURE_STORAGE_KEY" --output none

# Upload each training form to the sampleforms container as a blob
az storage blob upload-batch -d sampleforms -s "$SAMPLE_FORMS_DIR" --account-name "fabrikamform$unique_id" --auth-mode key --account-key "$AZURE_STORAGE_KEY" --output none

# Set a variable value for future use
STORAGE_ACCT_NAME="fabrikamform$unique_id"

# Get a Shared Access Signature (a signed URI that points to one or more storage resources) for the blobs in sampleforms
SAS_TOKEN=$(az storage container generate-sas --account-name "fabrikamform$unique_id" --name sampleforms --expiry "$expiry_date" --permissions rwl --auth-mode key --account-key "$AZURE_STORAGE_KEY")
URI="https://$STORAGE_ACCT_NAME.blob.core.windows.net/sampleforms?$SAS_TOKEN"

# Print the generated SAS URI, which authorizes access to the training data
echo "-------------------------------------"
echo "Storage account: $STORAGE_ACCT_NAME"
echo "SAS URI: $URI"
