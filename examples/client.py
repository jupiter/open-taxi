import json
import boto3

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

iot_host = 'a1hkcuoy1ihzp9.iot.eu-west-1.amazonaws.com'


def get_credentials_for_role(role_name, client_id):
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']

    # Create a more restricted policy
    iam_resource = boto3.resource('iam')
    role = iam_resource.Role(role_name)

    merged_policy_document = None

    for policy in role.policies.all():
        if merged_policy_document == None:
            merged_policy_document = policy.policy_document
        else:
            for statement in policy.policy_document['Statement']:
                merged_policy_document['Statement'].append(statement)

    restricted_connect_by_client_id = False
    for statement in merged_policy_document['Statement']:
        if statement.get('Sid') == 'OpenConnectStatement':
            statement['Resource'] = f'arn:aws:iot:*:{account_id}:client/{client_id}'
            restricted_connect_by_client_id = True

    assert restricted_connect_by_client_id

    merged_policy_json = json.dumps(merged_policy_document, indent=2)

    # Get credentials
    temporary_credentials = sts.assume_role(
        RoleArn=role.arn,
        RoleSessionName=client_id,
        Policy=merged_policy_json
    )
    return temporary_credentials['Credentials']

def get_client(client_id, temporary_credentials):
    myMQTTClient = AWSIoTMQTTClient(client_id, useWebsocket=True)
    myMQTTClient.configureEndpoint(iot_host, 443)
    myMQTTClient.configureCredentials('./certs/VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem')
    myMQTTClient.configureIAMCredentials(
        temporary_credentials['AccessKeyId'],
        temporary_credentials['SecretAccessKey'],
        temporary_credentials['SessionToken']
    )
    myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    return myMQTTClient
