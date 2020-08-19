import io
import json
import logging
from textwrap import dedent as _
from ruamel.yaml import YAML

from jupyter_telemetry.eventlog import EventLog

import pytest


SCHEMA_ID = "test.event"
VERSION = 1

@pytest.fixture
def schema():
    return  {
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
            'id': {
                'description': 'user ID',
                'categories': ['user-identifier'],
                'type': 'string'
            },
            'email': {
                'description': 'email address',
                'categories': ['user-identifiable-information'],
                'type': 'string'
            },
        }
    }


def test_raised_exception_for_nonlist_categories():
    # Bad schema in yaml form.
    yaml_schema = _("""\
    $id: test.schema
    title: Test Event
    version: 1
    type: object
    properties:
      test_property:
        description: testing a property
        categories: user-identifier
        type: string
    """)
    yaml = YAML(typ='safe')
    schema = yaml.load(yaml_schema)

    # Register schema with an EventLog
    e = EventLog(
        allowed_schemas={
            SCHEMA_ID: {
                "allowed_categories": ["user-identifier"]
            }
        },
    )

    # This schema does not have categories as a list.
    with pytest.raises(ValueError) as err:
        e.register_schema(schema)
    # Verify that the error message is the expected error message.
    assert 'must be a list.' in str(err.value)


def test_raised_exception_for_categories_with_more_than_restricted():
    # Bad schema in yaml form.
    yaml_schema = _("""\
    $id: test.schema
    title: Test Event
    version: 1
    type: object
    properties:
      test_property:
        description: testing a property
        categories:
            - unrestricted
            - random-category
        type: string
    """)
    yaml = YAML(typ='safe')
    schema = yaml.load(yaml_schema)

    # Register schema with an EventLog
    e = EventLog(
        allowed_schemas={
            SCHEMA_ID: {
                "allowed_categories": ["random-category"]
            }
        },
    )

    # This schema does not have categories as a list.
    with pytest.raises(ValueError) as err:
        e.register_schema(schema)
    # Verify that the error message is the expected error message.
    assert '`unresticted` is a special category' in str(err.value)


def test_missing_categories_label():
    # Bad schema in yaml form.
    yaml_schema = _("""\
    $id: test.schema
    title: Test Event
    version: 1
    type: object
    properties:
      test_property:
        description: testing a property
        type: string
    """)
    yaml = YAML(typ='safe')
    schema = yaml.load(yaml_schema)

    # Register schema with an EventLog
    e = EventLog(
        allowed_schemas={
            SCHEMA_ID: {
                "allowed_categories": ["random-category"]
            }
        }
    )

    # This schema does not have categories as a list.
    with pytest.raises(KeyError) as err:
        e.register_schema(schema)
    # Verify that the error message is the expected error message.
    assert 'All properties must have a "categories"' in str(err.value)


@pytest.mark.parametrize(
    'allowed_schemas,expected_recorded_props',
    [
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {"allowed_categories": []}},
            # Expected properties in the recorded event
            {'nothing-exciting'}
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {"allowed_categories": ["unrestricted"]}},
            # Expected properties in the recorded event
            {'nothing-exciting'}
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {"allowed_categories": ["user-identifier"]}},
            # Expected properties in the recorded event
            {'nothing-exciting', 'id'}
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {"allowed_categories": ["user-identifiable-information"]}},
            # Expected properties in the recorded event
            {'nothing-exciting', 'email'}
        ),
        (
            # User configuration for allowed_schemas
            {
                SCHEMA_ID: {
                    "allowed_categories": [
                        "user-identifier",
                        "user-identifiable-information"
                    ]
                }
            },
            # Expected properties in the recorded event
            {'nothing-exciting', 'email', 'id'}
        )
    ]
)
def test_category_filtering(schema, allowed_schemas, expected_recorded_props):
    sink = io.StringIO()

    # Create a handler that captures+records events with allowed tags.
    handler = logging.StreamHandler(sink)

    e = EventLog(
        handlers=[handler],
        allowed_schemas=allowed_schemas
    )
    e.register_schema(schema)

    event = {
        'nothing-exciting': 'hello, world',
        'id': 'test id',
        'email': 'test@testemail.com',
    }

    # Record event and read output
    e.record_event(SCHEMA_ID, VERSION, event)
    recorded_event = json.loads(sink.getvalue())
    recorded_props = set([key for key in recorded_event if not key.startswith('__')])
    # Verify that *exactly* the right properties are recorded.
    assert expected_recorded_props == recorded_props

