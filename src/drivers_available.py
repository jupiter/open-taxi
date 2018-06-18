import copy
import json

from opentaxi import iot, geo, validate


validator = validate.get_validator('./schemas/ot_drivers_broadcast.json')

def handler(event, context):
    if not validate.is_valid_message(validator, event):
        return {} # Discard event

    print(event)
    client = iot.get_client()

    # Send search topics to driver
    search_range_meters = 1500
    search_levels = [12, 16]
    search_max_cells = 20
    search_cellids = geo.get_cellids_in_range(
        event['lat_lng'][0],
        event['lat_lng'][1],
        search_range_meters,
        search_levels[0], search_levels[1],
        search_max_cells,
        2
    )
    search_topics = []
    for cellid in search_cellids:
        tokens = geo.get_hierarchy_as_tokens(cellid, placeholder=None)
        subtopics = '/'.join(map(str, tokens))
        search_topics.append(f'ot/riders/searching/{subtopics}/#')

    reply_topic = event['reply_topic']
    reply_message = {
        'type': 'riders_in_range',
        'lat_lng': event['lat_lng'],
        'range_meters': search_range_meters,
        'search_topics': search_topics
    }
    client.publish(reply_topic, json.dumps(reply_message), 1)

    # Broadcast to one cell
    # FUTURE: multiple cells along predicted line of travel
    broadcast_cellid = geo.get_cellid_at_level(
        event['lat_lng'][0],
        event['lat_lng'][1],
        16
    )
    broadcast_message = copy.deepcopy(event)
    del broadcast_message['auth_client_id']
    broadcast_tokens = geo.get_hierarchy_as_tokens(broadcast_cellid)
    broadcast_subtopics = '/'.join(map(str, broadcast_tokens))
    broadcast_topic = f'ot/drivers/available/{broadcast_subtopics}'
    client.publish(broadcast_topic, json.dumps(broadcast_message), 1)

    return {}
