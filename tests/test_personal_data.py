import io
import json
import logging
from textwrap import dedent as _
from ruamel.yaml import YAML

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
    personal-data: true
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
        allowed_schemas=[schema_id],
        collect_personal_data=False,
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
    personal-data: true
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
        allowed_schemas=[schema_id],
        collect_personal_data=False,
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
    personal-data: true
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
        allowed_schemas=[schema_id],
        collect_personal_data=False,
    )

    # This schema does not have categories as a list.
    with pytest.raises(KeyError) as err:
        e.register_schema(schema)
    # Verify that the error message is the expected error message.
    assert 'All properties must have a "categories"' in str(err.value)


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

