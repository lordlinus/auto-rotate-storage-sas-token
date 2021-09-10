import json
import logging
import os

import azure.functions as func
from TriggerKeyRotation import run

def main(event: func.EventGridEvent):
    event_json = event.get_json()
    result = json.dumps(
        {
            "id": event.id,
            "data": event_json,
            "topic": event.topic,
            "subject": event.subject,
            "event_type": event.event_type,
        }
    )
    logging.info("Python EventGrid trigger processed an event: %s", result)

    rg = os.getenv("ResourceGroup")
    keyvault_name = os.getenv("KeyVaultName")
    subscription_id = os.getenv("SubscriptionId")
    client_id = os.getenv("ClientId")
    storage_account = event_json["ObjectName"].split("-")[0]
    storage_container = event_json["ObjectName"].split("-")[1]
    mesg = ''
    if (
        event.event_type == "Microsoft.KeyVault.SecretExpired"
        or event.event_type == "Microsoft.KeyVault.SecretExpiresSoon"
    ):
        mesg = run(
            resource_group=rg,
            keyvault_name=keyvault_name,
            storage_account=storage_account,
            storage_container=storage_container,
            subscription_id=subscription_id,
        )
    elif event.event_type == "Microsoft.KeyVault.SecretNewVersionCreated":
        mesg = f"A new SAS version created:  {event.get_json()}"
    else:
        mesg = f"Event Type: {event.event_type} \
                 Event_info: {event_json}"
    logging.info(mesg)
    return mesg
