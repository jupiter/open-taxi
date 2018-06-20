import json
from jsonschema import Draft3Validator


def get_validator(schema_file_path):
    with open(schema_file_path, "r") as read_file:
        schema = json.load(read_file)
        if schema['properties'].get('reply_topic', False):
            schema['properties']['auth_client_id'] = {
                'type': 'string',
                'required': True
            } # Must be provided by rule's SQL statement
    return Draft3Validator(schema)


def is_valid_message(validator, message):
    invalid = []
    for error in validator.iter_errors(message):
        invalid.append(error.message)

    if len(invalid) > 0:
        print(json.dumps(message, sort_keys=True, indent=2))
        print(invalid)
        return False

    if message.get('reply_topic', False):
        auth_client_id = message['auth_client_id']
        possible_spoof = message['reply_topic'] != f'ot/replies/{auth_client_id}'
        if possible_spoof:
            return False

    return True
