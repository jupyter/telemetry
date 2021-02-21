import io
import json
import logging
from copy import deepcopy
from textwrap import dedent as _
from ruamel.yaml import YAML

from jupyter_telemetry.eventlog import EventLog

import pytest


SCHEMA_ID = 'test.event'
VERSION = 1


NESTED_CATEGORY_SCHEMA = {
    '$id': SCHEMA_ID,
    'title': 'Test Event',
    'version': VERSION,
    'description': 'Test Event.',
    'type': 'object',
    'properties': {
        'nothing-exciting': {
            'description': 'a property with nothing exciting happening',
            'categories': ['unrestricted'],
            'type': 'string'
        },
        'user': {
            'description': 'user',
            'categories': ['user-identifier'],
            'type': 'object',
            'properties': {
                'email': {
                    'description': 'email address',
                    'categories': ['user-identifiable-information'],
                    'type': 'string'
                },
                'id': {
                    'description': 'user ID',
                    'type': 'string'
                }
            }
        }
    }
}


EVENT_DATA = {
    'nothing-exciting': 'hello, world',
    'user': {
        'id': 'test id',
        'email': 'test@testemail.com',
    }
}


@pytest.mark.parametrize(
    'allowed_schemas,expected_output',
    [
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': []}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': None
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': ['unrestricted']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': None
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': ['user-identifier']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': {
                    'id': 'test id',
                    'email': None
                }
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': ['user-identifiable-information']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': None
            }
        ),
        (
            # User configuration for allowed_schemas
            {
                SCHEMA_ID: {
                    'allowed_categories': [
                        'user-identifier',
                        'user-identifiable-information'
                    ]
                }
            },
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': {
                    'id': 'test id',
                    'email': 'test@testemail.com',
                }
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_properties': ['user']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': {
                    'id': 'test id',
                    'email': 'test@testemail.com',
                }
            }
        ),
        (
            # User configuration for allowed_schemas
            {
                SCHEMA_ID: {
                    'allowed_categories': ['user-identifiable-information'],
                }
            },
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': None
            }
        ),
    ]
)
def test_category_filtering(allowed_schemas, expected_output):
    sink = io.StringIO()

    # Create a handler that captures+records events with allowed tags.
    handler = logging.StreamHandler(sink)

    e = EventLog(
        handlers=[handler],
        allowed_schemas=allowed_schemas
    )
    e.register_schema(NESTED_CATEGORY_SCHEMA)

    # Record event and read output
    e.record_event(SCHEMA_ID, VERSION, EVENT_DATA)

    recorded_event = json.loads(sink.getvalue())
    event_data = {key: value for key, value in recorded_event.items() if not key.startswith('__')}

    # Verify that *exactly* the right properties are recorded.
    assert expected_output == event_data
