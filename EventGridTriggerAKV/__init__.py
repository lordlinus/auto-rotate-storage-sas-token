import json
import logging

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions
from azure.mgmt.storage import StorageManagementClient

# https://docs.microsoft.com/en-us/rest/api/storageservices/create-account-sas

subscription_id = '7c1d967f-37f1-4047-bef7-05af9aa80fe2'

def get_storage_keys(group_name, storage_account_name, credential=DefaultAzureCredential()):
    storage_client = StorageManagementClient(credential, subscription_id)
    storage_keys = storage_client.storage_accounts.list_keys(group_name, storage_account_name)
    storage_keys = {v.key_name: v.value for v in storage_keys.keys}
    print('\tKey 1: {}'.format(storage_keys['key1']))
    print('\tKey 2: {}'.format(storage_keys['key2']))
    return storage_keys['key1'], storage_keys['key2']

def get_storage_account_sas(storage_account_name, storage_account_key, permission, expiry=datetime.utcnow() + timedelta(hours=1)):
    sas_token = generate_account_sas(
        storage_account_name,
        storage_account_key,
        resource_types=ResourceTypes(object=True),
        permission=AccountSasPermissions(read=True),
        expiry=expiry)
    logging.info(f'\tSAS Token: {sas_token}')
    return sas_token

def main(event: func.EventGridEvent):
    event_json = json.loads(event.get_json())
    result = json.dumps({
        'id': event.id,
        'data': event_json,
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })
    logging.info('Python EventGrid trigger processed an event: %s', result)

    credential = DefaultAzureCredential()
    storage_account = event_json['ObjectName'].split('-')[0]
    storage_container = event_json['ObjectName'].split('-')[1]

    key_client = KeyClient(vault_url="https://sattiraju-kv-01.vault.azure.net/", credential=credential)
    # service = BlobServiceClient(account_url=f"https://{storage_account}.blob.core.windows.net/", credential=credential)
    logging.info(f"EventGridTriggerAKV: {result}")
    k1,k2 = get_storage_keys('sattiraju-rg', storage_account)
    logging.info(f'\tKey 1: {k1}')
    logging.info(f'\tKey 2: {k2}')
    sas_token = get_storage_account_sas(storage_account, k1, 'r')
    logging.info(f'\tSAS Token: {sas_token}')

    key_client.set_key("storage_sas_key",sas_token)

    # storage_secret_key = key_client.get_secrets(event_json['ObjectName'])
    # logging.info(storage_secret_key.value)