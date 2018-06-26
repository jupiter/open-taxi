import boto3
import json
from datetime import datetime
from os import environ
import string
import random
from hashlib import sha256

from opentaxi import validate

base_validator = validate.get_validator('./schemas/ot_api_base_event.json')

sts = boto3.client('sts')
db_client = boto3.resource('dynamodb').Table(environ['REGS_TABLE_NAME'])

def handler(event, context):
    if not validate.is_valid_message(base_validator, event):
        return {} # Discard event

    path_params = event.get('pathParameters', {})
    body = json.loads(event.get('body', ''))

    invalid = []
    if body != None and not 'auth_code' in body:
        invalid.append('auth_code is a required query string parameter')
    if not 'reg_id' in path_params:
        invalid.append('reg_id is a required path parameter')
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

    reg_id = path_params['reg_id']
    reg = db_client.get_item(Key={'reg_id': reg_id}).get('Item')
    if reg == None:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'error': {
                    'message': 'Not found'
                }
            })
        }

    auth_code = body['auth_code']
    auth_code_hash = sha256(reg_id.encode() + auth_code.encode()).hexdigest()
    if reg['auth_code_hash'] != auth_code_hash:
        return {
            'statusCode': 403,
            'body': json.dumps({
                'error': {
                    'message': 'Incorrect code provided'
                }
            })
        }

    next_auth_code = ''.join([random.choice(string.digits + string.ascii_letters) for n in range(40)])
    next_auth_code_hash = sha256(reg_id.encode() + next_auth_code.encode()).hexdigest()

    is_driver = 'driver' in reg['profile']
    role_id = environ['DRIVERS_ROLE_ID'] if is_driver else environ['RIDERS_ROLE_ID']
    role_arn = environ['DRIVERS_ROLE_ARN'] if is_driver else environ['RIDERS_ROLE_ARN']
    user_id = f'{role_id}:{reg_id}'

    result = db_client.update_item(
        Key={
            'reg_id': reg_id
        },
        AttributeUpdates={
            'auth_code_hash': {
                'Value': next_auth_code_hash
            },
            'authenticated_user_id': {
                'Value': user_id
            },
            'authenticated_at': {
                'Value': datetime.now().__str__()
            },
            'expires_epoch': {
                'Value': 0
            }
        }
    )

    duration_seconds = 3600
    credentials = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=reg_id,
        DurationSeconds=duration_seconds
    )['Credentials']

    return {
        'statusCode': 200,
        'body': json.dumps({
            'next_auth_code': next_auth_code,
            'access_key_id': credentials['AccessKeyId'],
            'secret_access_key': credentials['SecretAccessKey'],
            'session_token': credentials['SessionToken'],
            'duration_seconds': duration_seconds,
            'user_id': user_id
        })
    }
