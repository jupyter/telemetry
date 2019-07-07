from contextlib import redirect_stderr
import json
import jsonschema
import logging
import pytest
import io

from jupyter_telemetry.eventlog import EventLog


def test_register_invalid():
    """
    Test registering invalid schemas fails
    """
    el = EventLog()
    with pytest.raises(jsonschema.SchemaError):
        el.register_schema({
            # Totally invalid
            'properties': True
        })

    with pytest.raises(ValueError):
        el.register_schema({
            'properties': {}
        })

    with pytest.raises(ValueError):
        el.register_schema({
            '$id': 'something',
            '$version': 1,
            'properties': {
                'timestamp': {
                    'type': 'string'
                }
            }
        })



def test_record_event():
    """
    Test emitting basic events works
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


def test_allowed_schemas():
    """
    Test no events are emitted if schema isn't explicitly allowed
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
    Test failure when event doesn't match schema
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