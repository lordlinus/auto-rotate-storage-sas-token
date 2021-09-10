# Rotate Storage SAS token based on HTTP trigger or using Azure Event Grid triggers

## Overview

Azure Key Vault sends events when the secrets are about to be expired and when they are expired, capturing these events using Azure Functions is a great way to automate the rotation of secrets automatically.Since Azure functions can also be triggered by HTTP requests you can include both manual ( HTTP trigger) and auto ( Event grid trigger ) to manage your secrets.

![Automate the rotation of a secret for resources that have two sets of authentication credentials](https://docs.microsoft.com/en-us/azure/key-vault/media/secrets/rotation-dual/rotation-diagram.png)

## How to use

- Enable event grid triggers for Azure Key Vault. [Monitoring Key Vault with Azure Event Grid](https://docs.microsoft.com/en-us/azure/key-vault/general/event-grid-overview)
- Create Azure functions `EventGrifTriggerAKV` and `TriggerKeyRotation` functions from this repo
- Assign system identity to the functions and ensure the storage account and key vault have required permission to this identity
- Trigger the functions by HTTP request or by Event Grid events
  - For HTTP request, use the following URL: `https://<your-function-app>.azurewebsites.net/api//TriggerKeyRotation\?storage_account\=####\&container\=####\&resource_group\=####\&keyvault_name\=####` (replace `####` with the actual values)

## Refrences

- Azure Functions: [Getting Started](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python)
- Azure Key Vault: [Overview](https://docs.microsoft.com/en-us/azure/key-vault/general/overview)
- Automate roration of secrets: [Overview](https://docs.microsoft.com/en-us/azure/key-vault/secrets/tutorial-rotation)
