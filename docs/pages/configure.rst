.. _using-telemetry:

Using telemetry in Jupyter applications
=======================================

Most people will use ``jupyter_telemetry`` to log events data from Jupyter applications, (e.g. JupyterLab, Jupyter Server, JupyterHub, etc).

In this case, you'll be able to record events provided by schemas within those applications. To start, you'll need to configure each application's ``EventLog`` object.

This usually means two things:

1. Define a set of ``logging`` handlers (from Python's standard library) to tell telemetry where to send your event data (e.g. file, remote storage, etc.)
2. List the names of events to collect and the properties/categories to collect from each of those events. (see the example below for more details).

Here is an example of a Jupyter configuration file, e.g. ``jupyter_config.d``, that demonstrates how to configure an eventlog.

.. code-block:: python

    from logging import FileHandler

    # Log events to a local file on disk.
    handler = FileHandler('events.txt')

    # Explicitly list the types of events
    # to record and what properties or what categories
    # of data to begin collecting.
    allowed_schemas = {
        "uri.to.schema": {
            "properties": ["name", "email"],
            "categories": ["HIPPA-required"]
        }
    }

    c.EventLog.handlers = [handler]
    c.EventLog.allowed_schemas = allowed_schemas