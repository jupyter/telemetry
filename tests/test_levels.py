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
            'id': {
                'description': 'user ID', 
                'level': 'confidential',
                'type': 'string'
            },
            'email': {
                'description': 'email address',
                'level': 'secret',
                'type': 'string'
            },
            'name': { 
                'description': 'name of user',
                'level': 'top_secret',
                'type': 'string'
            }
        }
    }


@pytest.mark.parametrize(
    'level,expected_props',
    [
        ('unclassified', set()),
        ('confidential', {'id'}),
        ('secret', {'id', 'email'}),
        ('top_secret', {'id', 'email', 'name'})
    ]
)
def test_drop_sensitive_properties(schema, schema_id, version, level, expected_props):
    sink = io.StringIO()
    handler = logging.StreamHandler(sink)
    # Set the event level
    handler.event_level = level

    e = EventLog(
        handlers=[handler],
        allowed_schemas=[schema_id]
    )
    e.register_schema(schema)

    event = {
        'id': 'test id',
        'email': 'test@testemail.com',
        'name': 'test name'
    }

    # Get a set of keys that should be missing
    dropped_props = set(event.keys()) - expected_props

    # Record event and read output
    e.record_event(schema_id, version, event)
    recorded_event = json.loads(sink.getvalue())
    recorded_props = set(recorded_event.keys())

    # Assert that sensitive properties are dropped.
    assert len(dropped_props.intersection(recorded_props)) == 0
    