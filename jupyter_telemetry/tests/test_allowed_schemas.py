from textwrap import dedent as _
from ruamel.yaml import YAML

from jupyter_telemetry.eventlog import EventLog

import pytest

from .utils import get_event_data


SCHEMA_ID = "test.event"
VERSION = 1


@pytest.fixture
def schema():
    return {
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


EVENT_DATA = {
    'nothing-exciting': 'hello, world',
    'id': 'test id',
    'email': 'test@testemail.com',
}


@pytest.mark.parametrize(
    'allowed_schemas,expected_output',
    [
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {"allowed_categories": []}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'id': None,
                'email': None,
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {"allowed_categories": ["unrestricted"]}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'id': None,
                'email': None,
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {"allowed_categories": ["user-identifier"]}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'id': 'test id',
                'email': None,
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {"allowed_categories": ["user-identifiable-information"]}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'id': None,
                'email': 'test@testemail.com',
            }
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
            {
                'nothing-exciting': 'hello, world',
                'id': 'test id',
                'email': 'test@testemail.com',
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {"allowed_properties": ["id"]}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'id': 'test id',
                'email': None,
            }
        ),
        (
            # User configuration for allowed_schemas
            {
                SCHEMA_ID: {
                    "allowed_properties": ["id"],
                    "allowed_categories": ["user-identifiable-information"],
                }
            },
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'id': 'test id',
                'email': 'test@testemail.com',
            }
        ),
    ]
)
def test_allowed_schemas(schema, allowed_schemas, expected_output):
    event_data = get_event_data(
        EVENT_DATA,
        schema,
        SCHEMA_ID,
        VERSION,
        allowed_schemas
    )

    # Cope with python3.12
    if "taskName" in event_data:
        del event_data["taskName"]

    # Verify that *exactly* the right properties are recorded.
    assert expected_output == event_data
