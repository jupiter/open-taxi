import time
from datetime import datetime
import json
import client
from search import update_subscriptions, print_updated_locations


def custom_callback(_client, _userdata, message):
    payload = json.loads(message.payload)
    if payload.get('type') == 'drivers_in_range':
        update_subscriptions(mqtt, payload, custom_callback)
    elif 'ot/drivers/available' in message.topic:
        print_updated_locations(payload)
    else:
        print("--------------")
        print(message.topic, ':')
        print(payload)
        print("--------------")

client_id = 'example-rider'
reply_topic = f'ot/replies/{client_id}'
temporary_credentials = client.get_credentials_for_role('open-taxi-sls-RidersRole-38MMK5V1PBN4', client_id)
mqtt = client.get_client(client_id, temporary_credentials)

mqtt.connect()

print('subscribing to', reply_topic)
mqtt.subscribe(reply_topic, 1, custom_callback)
time.sleep(2)

start_time = datetime.now()

while True:
    broadcast_message = {
        'reply_topic': reply_topic,
        'device_time': datetime.now().__str__(),
        'status': 'searching',
        'age_secs': (datetime.now() - start_time).seconds,
        'range_meters': 1500,
        'lat_lng': [51.507351, -0.127758]
    }
    broadcast_topic = 'ot/riders/broadcast'
    mqtt.publish(broadcast_topic, json.dumps(broadcast_message), 1)
    print('published to', broadcast_topic)
    time.sleep(15)

# mqtt.disconnect()
