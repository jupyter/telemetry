.. telemetry documentation master file, created by
   sphinx-quickstart on Fri Sep 27 16:34:00 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Jupyter Telemetry
=================

**Configurable event-logging for Jupyter applications and extensions.**


Telemetry provides a configurable traitlets object, EventLog, for structured event-logging in Python. It leverages Python's standard logging library for filtering, handling, and recording events. All events are validated (using jsonschema) against registered JSON schemas.

If you're looking for telemetry in Jupyter frontend applications (like JupyterLab), checkout the work happening in jupyterlab-telemetry_!

.. _jupyterlab-telemetry: https://github.com/jupyterlab/jupyterlab-telemetry


Installation
------------

Jupyter's Telemetry library can be installed from PyPI.

.. code-block::

    pip install jupyter_telemetry

Basic Usage
-----------

Here's a basic example of an EventLog.

.. code-block:: python

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


EventLog has two configurable traits:

    - ``handlers``: a list of Python's logging handlers.
    - ``allowed_schemas``: a list of event schemas to record.

Event schemas must be registered with the EventLog for events to be recorded. An event schema looks something like:

.. code-block:: json

    {
        "$id": "url.to.event.schema",
        "title": "My Event",
        "description": "All events must have a name property.",
        "type": "object",
        "properties": {
            "name": {
                "title": "Name",
                "description": "Name of event",
                "type": "string"
            }
        },
        "required": ["name"],
        "version": 1
    }


Two fields are required:

    - ``$id``: a valid URI to identify the schema (and possibly fetch it from a remote address).
    - ``version``: the version of the schema.

The other fields follow standard JSON schema structure.

Schemas can be registered from a Python dict object, a file, or a URL. This example loads the above example schema from file.

.. code-block:: python

    # Record an example event.
    event = {'name': 'example event'}
    eventlog.record_event(
        schema_id='url.to.event.schema',
        version=1,
        event=event
    )


.. toctree::
   :maxdepth: 2
   :caption: Table of Contents:

   pages/writing-a-schema
   pages/sphinxext

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
