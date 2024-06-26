import io
import json
import logging
import tempfile

import jsonschema
from datetime import datetime, timedelta
import pytest
from ruamel.yaml import YAML

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
            '$version': 1,  # This should been 'version'
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
                    'type': 'string',
                    'categories': ['unrestricted']
                },
            },
        })


def test_timestamp_override():
    """
    Simple test for overriding timestamp
    """
    schema = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string',
                'categories': ['unrestricted']
            },
        },
    }

    output = io.StringIO()
    handler = logging.StreamHandler(output)
    el = EventLog(handlers=[handler])
    el.register_schema(schema)
    el.allowed_schemas = ['test/test']

    timestamp_override = datetime.utcnow() - timedelta(days=1)
    el.record_event('test/test', 1, {
        'something': 'blah',
    }, timestamp_override=timestamp_override)
    handler.flush()

    event_capsule = json.loads(output.getvalue())

    # Cope with python3.12
    if "taskName" in event_capsule:
        del event_capsule["taskName"]

    assert event_capsule['__timestamp__'] == timestamp_override.isoformat() + 'Z'


def test_record_event():
    """
    Simple test for emitting valid events
    """
    schema = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string',
                'categories': ['unrestricted']
            },
        },
    }

    output = io.StringIO()
    handler = logging.StreamHandler(output)
    el = EventLog(handlers=[handler])
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

    # Cope with python3.12
    if "taskName" in event_capsule:
        del event_capsule["taskName"]

    assert event_capsule == {
        '__schema__': 'test/test',
        '__schema_version__': 1,
        '__metadata_version__': 1,
        'something': 'blah'
    }


def test_register_schema_file(tmp_path):
    """
    Register schema from a file
    """
    schema = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string',
                'categories': ['unrestricted']
            },
        },
    }

    el = EventLog()

    yaml = YAML(typ='safe')

    schema_file = tmp_path.joinpath("schema.yml")
    yaml.dump(schema, schema_file)
    el.register_schema_file(str(schema_file))

    assert schema in el.schemas.values()


def test_register_schema_file_object(tmp_path):
    """
    Register schema from a file
    """
    schema = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string',
                'categories': ['unrestricted']
            },
        },
    }

    el = EventLog()

    yaml = YAML(typ='safe')

    schema_file = tmp_path.joinpath("schema.yml")
    yaml.dump(schema, schema_file)
    with open(str(schema_file), 'r') as f:
        el.register_schema_file(f)

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
                'type': 'string',
                'categories': ['unrestricted']
            },
        },
    }

    output = io.StringIO()
    handler = logging.StreamHandler(output)
    el = EventLog(handlers=[handler])
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
                'type': 'string',
                'categories': ['unrestricted']
            },
            'status': {
                'enum': ['success', 'failure'],
                'categories': ['unrestricted']
            }
        }
    }

    el = EventLog(handlers=[logging.NullHandler()])
    el.register_schema(schema)
    el.allowed_schemas = ['test/test']

    with pytest.raises(jsonschema.ValidationError):
        el.record_event('test/test', 1, {
            'something': 'blah',
            'status': 'hi'  # 'not-in-enum'
        })


def test_unique_logger_instances():
    schema0 = {
        '$id': 'test/test0',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string',
                'categories': ['unrestricted']
            },
        },
    }

    schema1 = {
        '$id': 'test/test1',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string',
                'categories': ['unrestricted']
            },
        },
    }

    output0 = io.StringIO()
    output1 = io.StringIO()
    handler0 = logging.StreamHandler(output0)
    handler1 = logging.StreamHandler(output1)

    el0 = EventLog(handlers=[handler0])
    el0.register_schema(schema0)
    el0.allowed_schemas = ['test/test0']

    el1 = EventLog(handlers=[handler1])
    el1.register_schema(schema1)
    el1.allowed_schemas = ['test/test1']

    el0.record_event('test/test0', 1, {
        'something': 'blah',
    })
    el1.record_event('test/test1', 1, {
        'something': 'blah',
    })
    handler0.flush()
    handler1.flush()

    event_capsule0 = json.loads(output0.getvalue())

    assert '__timestamp__' in event_capsule0
    # Remove timestamp from capsule when checking equality, since it is gonna vary
    del event_capsule0['__timestamp__']
    # Cope with python3.12
    if "taskName" in event_capsule0:
        del event_capsule0["taskName"]
    assert event_capsule0 == {
        '__schema__': 'test/test0',
        '__schema_version__': 1,
        '__metadata_version__': 1,
        'something': 'blah'
    }

    event_capsule1 = json.loads(output1.getvalue())

    assert '__timestamp__' in event_capsule1
    # Remove timestamp from capsule when checking equality, since it is gonna vary
    del event_capsule1['__timestamp__']
    # Cope with python3.12
    if "taskName" in event_capsule1:
        del event_capsule1["taskName"]
    assert event_capsule1 == {
        '__schema__': 'test/test1',
        '__schema_version__': 1,
        '__metadata_version__': 1,
        'something': 'blah'
    }


def test_register_duplicate_schemas():
    schema0 = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'something': {
                'type': 'string',
                'categories': ['unrestricted']
            },
        },
    }

    schema1 = {
        '$id': 'test/test',
        'version': 1,
        'properties': {
            'somethingelse': {
                'type': 'string',
                'categories': ['unrestricted']
            },
        },
    }

    el = EventLog()
    el.register_schema(schema0)
    with pytest.raises(ValueError):
        el.register_schema(schema1)
