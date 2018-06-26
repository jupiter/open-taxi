import boto3
import json
import time
import random
import string
from os import environ
from uuid import uuid4
from hashlib import sha256

from opentaxi import validate

base_validator = validate.get_validator('./schemas/ot_api_base_event.json')
validator = validate.get_validator('./schemas/ot_api_registration.json')

expires_in_secs = 900 # 15 minutes

db_client = boto3.resource('dynamodb').Table(environ['REGS_TABLE_NAME'])
sns_client = boto3.client('sns')

def handler(event, context):
    if not validate.is_valid_message(base_validator, event):
        return {} # Discard event

    body = json.loads(event.get('body', ''))

    invalid = validate.validate(validator, body)
    if len(invalid) > 0:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': {
                    'message': 'Invalid request',
                    'details': invalid
                }
            })
        }

    phone_number = None
    if 'driver' in body:
        # TODO: Check whether this driver has a valid license
        # TODO: Check whether this vehicle has a valid license
        phone_number = body['driver']['phone_number']
    elif 'rider' in body:
        phone_number = body['rider']['phone_number']

    reg_id = str(uuid4()).replace('-', '')
    auth_code = ''.join([random.choice(string.digits) for n in range(6)])
    auth_code_hash = sha256(reg_id.encode() + auth_code.encode()).hexdigest()

    db_client.put_item(
        Item={
            'reg_id': reg_id,
            'profile': body,
            'auth_code_hash': auth_code_hash,
            'expires_epoch': int(time.time()) + expires_in_secs
        }
    )

    response = sns_client.publish(
        PhoneNumber=phone_number,
        Message=f"Here's your code for OpenTaxi: {auth_code}",
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'id': reg_id
        })
    }
