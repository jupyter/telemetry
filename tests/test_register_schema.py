from contextlib import redirect_stderr
import json
import jsonschema
import logging
import pytest
import tempfile
from ruamel.yaml import YAML
import io

from jupyter_telemetry.eventlog import EventLog


def test_register_invalid_schema():
    """
    Invalid JSON Schemas should fail registration
    """
    el = EventLog()
    with pytest.raises(jsonschema.SchemaError):
        el.register_schema({
            # Totally invalid
            'properties': True
        })

def test_missing_required_properties():
    """
    id and $version are required properties in our schemas.

    They aren't required by JSON Schema itself
    """
    el = EventLog()
    with pytest.raises(ValueError):
        el.register_schema({
            'properties': {}
        })

    with pytest.raises(ValueError):
        el.register_schema({
            '$id': 'something',
            '$version': 1, # This should been 'version'
        })

def test_reserved_properties():
    """
    User schemas can't have properties starting with __

    These are reserved
    """
    el = EventLog()
    with pytest.raises(ValueError):
        el.register_schema({
            '$id': 'test/test',
            'version': 1,
            'properties': {
                '__fail__': {
                    'type': 'string'
                },
            },
        })

def test_record_event():
    """
    Simple test for emitting valid events
    """
    schema = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string'
            },
        },
    }

    output = io.StringIO()
    handler = logging.StreamHandler(output)
    el = EventLog(handlers_maker=lambda el: [handler])
    el.register_schema(schema)
    el.allowed_schemas = ['test/test']

    el.record_event('test/test', 1, {
        'something': 'blah',
    })
    handler.flush()

    event_capsule = json.loads(output.getvalue())

    assert '__timestamp__' in event_capsule
    # Remove timestamp from capsule when checking equality, since it is gonna vary
    del event_capsule['__timestamp__']
    assert event_capsule == {
        '__schema__': 'test/test',
        '__version__': 1,
        'something': 'blah'
    }

def test_register_schema_file():
    """
    Register schema from a file
    """
    schema = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string'
            },
        },
    }

    el = EventLog()

    yaml = YAML(typ='safe')
    with tempfile.NamedTemporaryFile(mode='w') as f:
        yaml.dump(schema, f)
        f.flush()

        f.seek(0)

        el.register_schema_file(f.name)

    assert schema in el.schemas.values()

def test_allowed_schemas():
    """
    Events should be emitted only if their schemas are allowed
    """
    schema = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string'
            },
        },
    }

    output = io.StringIO()
    handler = logging.StreamHandler(output)
    el = EventLog(handlers_maker=lambda el: [handler])
    # Just register schema, but do not mark it as allowed
    el.register_schema(schema)

    el.record_event('test/test', 1, {
        'something': 'blah',
    })
    handler.flush()


    assert output.getvalue() == ''

def test_record_event_badschema():
    """
    Fail fast when an event doesn't conform to its schema
    """
    schema = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string'
            },
            'status': {
                'enum': ['success', 'failure']
            }
        }
    }

    el = EventLog(handlers_maker=lambda el: [logging.NullHandler()])
    el.register_schema(schema)
    el.allowed_schemas = ['test/test']

    with pytest.raises(jsonschema.ValidationError):
        el.record_event('test/test', 1, {
            'something': 'blah',
            'status': 'not-in-enum'
        })