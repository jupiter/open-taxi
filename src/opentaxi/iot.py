import os

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


client = None

def get_client():
    global client
    if client == None:
        AccessKeyId = os.environ.get('AWS_ACCESS_KEY_ID')
        SecretKey = os.environ.get('AWS_SECRET_ACCESS_KEY')
        SessionToken = os.environ.get('AWS_SESSION_TOKEN')
        Host = os.environ.get('OT_IOT_HOST')

        client = AWSIoTMQTTClient("sharedClient", useWebsocket=True)
        client.configureEndpoint(Host, 443)
        client.configureCredentials("./certs/VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem")
        client.configureIAMCredentials(AccessKeyId, SecretKey, SessionToken)
        client.configureAutoReconnectBackoffTime(1, 32, 20)
        client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        client.configureDrainingFrequency(2)  # Draining: 2 Hz
        client.configureConnectDisconnectTimeout(10)  # 10 sec
        client.configureOfflinePublishQueueing(0)  # No offline Publish queueing
        client.configureConnectDisconnectTimeout(5)  # 5 sec
        client.configureMQTTOperationTimeout(5)  # 5 sec
        client.connect()
    return client
