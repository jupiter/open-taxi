import json
import datetime
import unittest
from unittest.mock import patch, Mock

from .drivers_available import handler
import opentaxi.iot


class DriversAvailableHandlerTests(unittest.TestCase):

    @patch('opentaxi.iot.get_client')
    def test_valid_input(self, get_client_patch):
        mock_client = Mock()
        get_client_patch.return_value = mock_client

        event = {
            'auth_client_id': 'abc123',
            'reply_topic': 'ot/replies/abc123',
            'device_time': datetime.datetime.now().__str__(),
            'status': 'available',
            'age_secs': 0,
            'lat_lng': [51.507351, -0.127758]
        }
        context = {}

        result = handler(event, context)

        self.assertTrue(get_client_patch.called)
        self.assertEqual(mock_client.publish.call_count, 2)
        self.assertEqual(mock_client.publish.call_args_list[0][0][0], 'ot/replies/abc123')
        reply_message = json.loads(mock_client.publish.call_args_list[0][0][1])
        search_topics_len = len(reply_message.get('search_topics', []))
        self.assertTrue(search_topics_len > 0)
        self.assertTrue(search_topics_len <= 21)
        self.assertEqual(reply_message['search_topics'][0], 'ot/riders/searching/487605/487604b/#')

        del reply_message['search_topics']
        self.assertEqual(reply_message, {
            'type': 'riders_in_range',
            'lat_lng': [51.507351, -0.127758],
            'range_meters': 1500
        })
        self.assertEqual(mock_client.publish.call_args_list[1][0][0], 'ot/drivers/available/487605/487604d/487604cf/487604ce3')
        self.assertEqual({}, result)
