last_range_message = None

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

    for topic in new_topics:
        print('subscribing to', topic)
        client.subscribeAsync(topic, 1, None, callback)

    for topic in old_topics:
        print('unsubscribing from', topic)
        client.unsubscribeAsync(topic)

    last_range_message = range_message
