Logging sensitive data
======================

Jupyter Telemetry requires that all fields in an event schema explicitly state when personally-identifiable information is being collected. Each property in an event schema must have a ``sensitivity_level`` attribute.

Since events may include data with varying degrees of sensitivity, Jupyter Telemetry uses a multi-level security approach. It exposed three levels of sensitivity:

    + ``'unrestricted'``
    + ``'personal-identifier'``
    + ``'personally-identifiable-information'``

Each event property can be given one of these three levels:

.. code-block:: yaml

    $id: example.schema
    ...
    sensitivity_level:
    properties:
      name:
        title: Name
        sensitivity_level: unrestricted
        description: Name of event
        type: string
      user:
        title: User name
        sensitivity_level: personal-identifier
        description: Name of the user who initiated the event.
      affiliation:
        title: I

Jupyter Telemetry uses ``sensitivity_level`` to drop sensitive data when emitting events. By default, properties greater than "unclassifed" are dropped from recorded event data.

Each logging handler increase the level of sensitive data it emots. This can be configured by changing its ``.event_level`` attribute.

.. code-block:: python

    import logging

    handler = logging.FileHandler('events.log')
    handler.event_level = 'secret'

