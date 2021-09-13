import os
import logging
import requests

import azure.functions as func
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from datetime import datetime, timedelta
from azure.storage.blob import (
    BlobServiceClient,
    generate_account_sas,
    ResourceTypes,
    AccountSasPermissions,
)
from azure.mgmt.storage import StorageManagementClient


def get_storage_keys(
    resource_group,
    storage_account_name,
    subscription_id,
    credential=DefaultAzureCredential(),
) -> (str,str):
    storage_client = StorageManagementClient(credential, subscription_id)
    storage_keys = storage_client.storage_accounts.list_keys(
        resource_group, storage_account_name
    )
    storage_keys = {v.key_name: v.value for v in storage_keys.keys}
    # print("\tKey 1: {}".format(storage_keys["key1"]))
    # print("\tKey 2: {}".format(storage_keys["key2"]))
    return storage_keys["key1"], storage_keys["key2"]


def get_storage_account_sas(
    storage_account_name,
    storage_account_key,
    permission=None,
    expiry=datetime.utcnow() + timedelta(hours=1),
) -> str:
    sas_token = generate_account_sas(
        storage_account_name,
        storage_account_key,
        resource_types=ResourceTypes(object=True),
        permission=AccountSasPermissions(read=True),
        expiry=expiry,
    )
    # logging.info(f"\tSAS Token: {sas_token}")
    return sas_token


def test_sas_token(storage_account_name, sas_token=None) -> bool:
    test_file_url = f"https://{storage_account_name}.blob.core.windows.net/data/test.txt?{sas_token}"
    r = requests.get(test_file_url)
    return True if r.status_code == 200 else False


def create_akv_key(keyvault_name, key_name, value, credential) -> (str,str):
    secret_client = SecretClient(
        vault_url=f"https://{keyvault_name}.vault.azure.net/", credential=credential
    )
    secret = secret_client.set_secret(
        key_name, value, expires_on=datetime.utcnow() + timedelta(hours=1)
    )
    return secret.properties.version, secret.properties.expires_on


def run(
    resource_group,
    storage_account,
    storage_container,
    keyvault_name,
    subscription_id=None,
) -> func.HttpResponse:
    credentials = ManagedIdentityCredential()
    k1, k2 = get_storage_keys(
        storage_account_name=storage_account,
        resource_group=resource_group,
        subscription_id=subscription_id,
    )
    sas_token = get_storage_account_sas(
        storage_account_name=storage_account, storage_account_key=k1
    )
    if test_sas_token(storage_account_name=storage_account, sas_token=sas_token):
        version, expires_on = create_akv_key(
            keyvault_name=keyvault_name,
            key_name=f"{storage_account}-{storage_container}-saskey",
            value=sas_token,
            credential=credentials,
        )
        return func.HttpResponse(f"This HTTP triggered function executed successfully. \
            A new SAS token is created and added to Azure Key Valut \
            version: {version} and expires at UTC: {expires_on}", status_code=200)
    else:
        return func.HttpResponse("This HTTP triggered function executed failed.", status_code=500)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    storage_account = req.params.get("storage_account")
    storage_container = req.params.get("container")
    rg = req.params.get("resource_group")
    keyvault_name = req.params.get("keyvault_name")
    subscription_id = os.getenv("SubscriptionId")

    response = run(
        resource_group=rg,
        storage_account=storage_account,
        storage_container=storage_container,
        keyvault_name=keyvault_name,
        subscription_id=subscription_id,
    )
    return response