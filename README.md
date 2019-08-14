# Telemetry

[![CircleCI](https://circleci.com/gh/jupyter/telemetry.svg?style=svg)](https://circleci.com/gh/jupyter/telemetry) 
[![codecov](https://codecov.io/gh/jupyter/telemetry/branch/master/graph/badge.svg)](https://codecov.io/gh/jupyter/telemetry)

Telemetry for Jupyter Applications and extensions.

## Basic Usage

Telemetry provides a configurable traitlets object, `EventLog`, for structured event-logging in Python. It leverages Python's standard `logging` library for filtering, handling, and recording events. All events are validated (using [jsonschema](https://pypi.org/project/jsonschema/)) againsted registered [JSON schemas](https://json-schema.org/). 

### Using the `EventLog`

Let's look at a basic example of an `EventLog`.
```python
import logging
from jupyter_telemetry import EventLog


eventlog = EventLog(
    # Use logging handlers to route where events
    # should be record.
    handlers=[
        logging.FileHandler('events.log')
    ],
    # List schemas of events that should be recorded.
    allowed_schemas=[
        'uri.to.event.schema'
    ]
)
```

EventLog has two configurable traits:
* `handlers`: a list of Python's `logging` handlers.
* `allowed_schemas`: a list of event schemas to record.

Event schemas must be registered with the `EventLog` for events to be recorded. An event schema looks something like:
```json
{
  '$id': 'url.to.event.schema',
  'title': 'My Event',
  'description': 'All events must have a name property.',
  'type': 'object',
  'properties': {
    'name': {
      'title': 'Name',
      'description': 'Name of event',
      'type': 'string'
    }
  },
  'required': ['name'],
  'version': 1
}
```
2 fields are required:
* `$id`: a valid URI to identify the schema (and possibly fetch it from a remote address).
* `version`: the version of the schema.

The other fields are follow standard JSON schema structure.

Schemas can be registered from a Python `dict` object, a file, or a URL. This example loads the above example schema from file.
```python
# Register the schema.
eventlog.register_schema_file('schema.json')
```

Events are recorded using the `record_event` method. This method validates the event data and routes the JSON string to the Python `logging` handlers listed in the `EventLog`.
```python
# Record an example event.
event = {'name': 'example event'}
eventlog.record_event(
    schema_id='url.to.event.schema',
    version=1,
    event=event
)
```

### Using PyDantic to define and validate events

Telemetry also works seamlessly with [pydantic](https://pydantic-docs.helpmanual.io/), a Python library useful for generating and validating schemas. Telemetry includes a convenient `Event` model (that subclasses pydantic's `BaseModel`) for defining+validating event schemas. 

The following example demonstrates how to define a custom event schema using the `Event` model.
```python
from pydantic import Schema
from jupyter_telemetry import Event


class MyEvent(Event):
    """All events must have a name property."""
    # Required schema metadata.
    _id = 'url.to.event.schema'
    _title = 'My Event'
    _version = 1
    
    # Define properties of event.
    name: str = Schema(
        ...,
        description="Name of event"
    )
```
The following class attributes are required:
* _id: the schema ID (a valid URI)
* _title: the title of the schema.
* _version: the version of the schema.

We can get the JSON schema of this object by calling the `.schema()` method:
```python
# Get schema of MyEvent
schema = MyEvent.schema()

# Print the schema as JSON.
import json
print(json.dumps(schema, indent=2))

# {
#   "title": "My Event",
#   "description": "All events must have a name property.",
#   "type": "object",
#   "properties": {
#     "name": {
#       "title": "Name",
#       "description": "Name of event",
#       "type": "string"
#     }
#   },
#   "required": [
#     "name"
#   ],
#   "$id": "url.to.event.schema",
#   "version": 1
# }
```
We can register `Event` schemas using the `.register_event_model()` method. Then, we can record instances of these events using the `.record_event_model()` method:
```python
# Register a custom pydantic event.
eventlog.register_event_model(MyEvent)

# Create an instance of the event. 
# pydantic handles validation.
event = MyEvent(name='My Event')

# Record the event.
eventlog.record_event_model(event)
```


## Install

Jupyter's Telemetry library can be installed from PyPI.
```
pip install jupyter_telemetry
```