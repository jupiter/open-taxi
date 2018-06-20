from datetime import datetime
from operator import itemgetter

last_range_message = None
locations_by_reply_topic = {}


def update_subscriptions(client, range_message, callback):
    new_topics = None
    old_topics = None
    global last_range_message

    if last_range_message == None:
        new_topics = range_message['topics']
        old_topics = []
    elif last_range_message['device_time'] < range_message['device_time']:
        new_topics = set(range_message['topics']) - set(last_range_message['topics'])
        old_topics = set(last_range_message['topics']) - set(range_message['topics'])
    else:
        # Duplicate or out of order
        return

    if len(new_topics) + len(old_topics) > 0:
        print('subscribing to', len(new_topics), 'and unsubscribing from', len(old_topics))

    for topic in new_topics:
        # print('subscribing to', topic)
        client.subscribeAsync(topic, 1, None, callback)

    for topic in old_topics:
        # print('unsubscribing from', topic)
        client.unsubscribeAsync(topic)

    last_range_message = range_message


def print_updated_locations(new_location):
    existing = locations_by_reply_topic.get(new_location['reply_topic'])

    if existing == None or existing['device_time'] < new_location['device_time']:
        new_location['updated_time'] = datetime.now()
        locations_by_reply_topic[new_location['reply_topic']] = new_location

    locations_list = []
    for key, value in locations_by_reply_topic.items():
        locations_list.append(value)

    locations_list.sort(key=itemgetter('updated_time'), reverse=True)
    for location in locations_list:
        print(
            location['reply_topic'],
            location.get('lat_lng', '?,?'),
            (datetime.now() - location['updated_time']).seconds,
            'secs ago'
        )
