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
        'personal-data': True,
        'properties': {
            'nothing-exciting': {
                'description': 'a property with nothing exciting happening',
                'category': 'unrestricted',
                'type': 'string'
            },
            'id': {
                'description': 'user ID',
                'category': 'user-identifier',
                'type': 'string'
            },
            'email': {
                'description': 'email address',
                'category': 'user-identifiable-information',
                'type': 'string'
            },
        }
    }


def test_collect_personal_data_false(schema, schema_id, version):
    sink = io.StringIO()

    # Create a handler that captures+records events with allowed tags.
    handler = logging.StreamHandler(sink)

    e = EventLog(
        handlers=[handler],
        allowed_schemas=[schema_id],
        collect_personal_data=False,
    )
    e.register_schema(schema)

    event = {
        'nothing-exciting': 'hello, world',
        'id': 'test id',
        'email': 'test@testemail.com',
    }

    # Record event and read output
    e.record_event(schema_id, version, event)
    assert sink.getvalue() == ''


@pytest.mark.parametrize(
    'categories,expected_props',
    [
        ([], {'nothing-exciting'}),
        (['unrestricted'], {'nothing-exciting'}),
        (['user-identifier'], {'nothing-exciting', 'id'}),
        (['user-identifiable-information'], {'nothing-exciting', 'email'}),
        (['user-identifier', 'user-identifiable-information'], {'nothing-exciting', 'email', 'id'})
    ]
)
def test_category_filtering(schema, schema_id, version, categories, expected_props):
    sink = io.StringIO()

    # Create a handler that captures+records events with allowed tags.
    handler = logging.StreamHandler(sink)

    e = EventLog(
        handlers=[handler],
        allowed_schemas=[schema_id],
        collect_personal_data=True,
        allowed_categories=categories
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

