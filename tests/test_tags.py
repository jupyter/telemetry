import io
import json
import logging

from jupyter_telemetry.eventlog import EventLog

import pytest


@pytest.fixture
def version(): return 1


@pytest.fixture()
def schema_id(): return 'test.event'


@pytest.fixture
def schema(schema_id, version):
    return  {
        '$id': schema_id,
        'title': 'Test Event',
        'version': version,
        'description': 'Test Event.',
        'type': 'object',
        'properties': {
            'nothing-exciting': {
                'description': 'a property with nothing exciting happening',
                'tag': 'unrestricted',
                'type': 'string'
            },
            'id': {
                'description': 'user ID',
                'tag': 'user-identifier',
                'type': 'string'
            },
            'email': {
                'description': 'email address',
                'tag': 'user-identifiable-information',
                'type': 'string'
            },
        }
    }


@pytest.mark.parametrize(
    'tags,expected_props',
    [
        ({'unrestricted'}, {'nothing-exciting'}),
        ({'user-identifier'}, {'nothing-exciting', 'id'}),
        ({'user-identifiable-information'}, {'nothing-exciting', 'email'})
    ]
)
def test_properties_tags(schema, schema_id, version, tags, expected_props):
    sink = io.StringIO()

    # Create a handler that captures+records events with allowed tags.
    handler = logging.StreamHandler(sink)
    handler.allowed_tags = tags

    e = EventLog(
        handlers=[handler],
        allowed_schemas=[schema_id]
    )
    e.register_schema(schema)

    event = {
        'nothing-exciting': 'hello, world',
        'id': 'test id',
        'email': 'test@testemail.com',
    }

    # Record event and read output
    e.record_event(schema_id, version, event)
    recorded_event = json.loads(sink.getvalue())
    recorded_props = set([key for key in recorded_event if not key.startswith('__')])

    assert expected_props == recorded_props

