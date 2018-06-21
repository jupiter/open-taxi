import json
import boto3

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

iot_host = 'a1hkcuoy1ihzp9.iot.eu-west-1.amazonaws.com'


def get_credentials_for_role(role_name, session_name):
    sts = boto3.client('sts')
    iam_resource = boto3.resource('iam')
    role = iam_resource.Role(role_name)

    # Get credentials
    credentials = sts.assume_role(
        RoleArn=role.arn,
        RoleSessionName=session_name,
        # Policy=merged_policy_json
    )['Credentials']
    client_id = f'{role.role_id}:{session_name}'

    return {
        'access_key_id': credentials['AccessKeyId'],
        'secret_access_key': credentials['SecretAccessKey'],
        'session_token': credentials['SessionToken'],
        'client_id': client_id
    }

def get_client(credentials):
    print(credentials['client_id'])
    myMQTTClient = AWSIoTMQTTClient(credentials['client_id'], useWebsocket=True)
    myMQTTClient.configureEndpoint(iot_host, 443)
    myMQTTClient.configureCredentials('./certs/VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem')
    myMQTTClient.configureIAMCredentials(
        credentials['access_key_id'],
        credentials['secret_access_key'],
        credentials['session_token']
    )
    myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    return myMQTTClient
