.. _adding-telemetry:

Adding telemetry to an application
==================================

Jupyter Telemetry enables you to log events from your running application. (It's designed to work best with traitlet's applications for simple configuration.) To use telemetry, begin by creating an instance of ``EventLog``:

.. code-block:: python


    from jupyter_telemetry import EventLog

    class MyApplication:

        def __init__(self):
            ...
            # The arguments
            self.eventlog = EventLog(
                ...
                # Either pass the traits (see below) here,
                # or enable users of your application to configure
                # the EventLog's traits.
            )


EventLog has two configurable traits:

    - ``handlers``: a list of Python's logging handlers that handle the recording of incoming events.
    - ``allowed_schemas``: a dictionary of options for each schema describing what data should be collected.

Next, you'll need to register event schemas for your application. You can register schemas using the ``register_schema_file`` (JSON or YAML format) or ``register_schema`` methods.


Once your have an instance of ``EventLog`` and your registered schemas, you can use the ``record`` method to log that event.

.. code-block:: python

    # Record an example event.
    event = {'name': 'example event'}
    self.eventlog.record_event(
        schema_id='url.to.event.schema',
        version=1,
        event=event
    )
