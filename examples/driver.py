import time
from datetime import datetime
import json
import client
from search import update_subscriptions, print_updated_locations


def custom_callback(_client, _userdata, message):
    payload = json.loads(message.payload)
    if payload.get('type') == 'riders_in_range':
        update_subscriptions(mqtt, payload, custom_callback)
    elif 'ot/riders/searching' in message.topic:
        print_updated_locations(payload)
    else:
        print("--------------")
        print(message.topic, ':')
        print(payload)
        print("--------------")

role_name = 'open-taxi-sls-DriversRole-1S0DSO6ZWQE9'
session_name = 'example-driver'
credentials = client.get_credentials_for_role(role_name, session_name)
client_id = credentials['client_id']
reply_topic = f'ot/replies/{client_id}'

mqtt = client.get_client(credentials)
mqtt.connect()

print('subscribing to', reply_topic)
mqtt.subscribe(reply_topic, 1, custom_callback)
time.sleep(2)

start_time = datetime.now()

path = [
    [51.509541, -0.076598],
    [51.509804, -0.088039],
    [51.511115, -0.096459],
    [51.510974, -0.107735],
    [51.509745, -0.118489],
    [51.507234, -0.126293],
]
path_iterator = iter(path)

while True:
    ll = next(path_iterator, path[-1])
    broadcast_message = {
        'reply_topic': reply_topic,
        'device_time': datetime.now().__str__(),
        'status': 'available',
        'age_secs': (datetime.now() - start_time).seconds,
        'range_meters': 1500,
        'lat_lng': ll
    }
    broadcast_topic = 'ot/drivers/broadcast'
    mqtt.publish(broadcast_topic, json.dumps(broadcast_message), 1)
    print('published', ll, 'to', broadcast_topic)
    time.sleep(15)

# mqtt.disconnect()
