import time
from datetime import datetime
import json
import client


def custom_callback(client, userdata, message):
    print("--------------")
    print(message.topic, ':')
    print(json.loads(message.payload))
    print("--------------")

client_id = 'example-driver'
reply_topic = f'ot/replies/{client_id}'
temporary_credentials = client.get_credentials_for_role('open-taxi-sls-DriversRole-1S0DSO6ZWQE9', client_id)
mqtt = client.get_client(client_id, temporary_credentials)

mqtt.connect()

print('subscribing to', reply_topic)
mqtt.subscribe(reply_topic, 1, custom_callback)
time.sleep(2)

while True:
    broadcast_message = {
        'reply_topic': reply_topic,
        'device_time': datetime.now().__str__(),
        'status': 'available',
        'age_secs': (datetime.now() - start_time).seconds,
        'lat_lng': [51.507351, -0.127758]
    }
    broadcast_topic = 'ot/drivers/broadcast'
    mqtt.publish(broadcast_topic, json.dumps(broadcast_message), 1)
    print('published to', broadcast_topic)
    time.sleep(30)

# mqtt.disconnect()
