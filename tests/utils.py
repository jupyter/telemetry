from copy import deepcopy
import io
import json
import logging

from jupyter_telemetry.eventlog import EventLog


def get_event_data(event, schema, *args, **kwargs):
    sink = io.StringIO()

    # Create a handler that captures+records events with allowed tags.
    handler = logging.StreamHandler(sink)

    e = EventLog(*args, **{**kwargs, 'handlers': [handler]})

    e.register_schema(schema)

    # Record event and read output
    e.record_event(schema['$id'], schema['version'], deepcopy(event))

    recorded_event = json.loads(sink.getvalue())
    return {key: value for key, value in recorded_event.items() if not key.startswith('__')}
