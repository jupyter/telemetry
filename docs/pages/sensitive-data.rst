Logging sensitive data
======================

Jupyter Telemetry offers flexibility when logging and handling sensitive data. 

Since events may include data with varying degrees of sensitivity, Jupyter Telemetry uses a multi-level security approach. It exposed four levels of sensitivity:

    + ``'unclassified'``
    + ``'confidential'``
    + ``'secret'``
    + ``'top_secret'``

Each event property can be given one of these four levels. This is reflected in the event JSON schema using the ``level`` attribute (if this property is missing from the schema, an error will be thrown):

.. code-block:: yaml

    $id: example.schema
    ...
    properties:
      name:
        title: Name
        level: confidential
        description: |
            Name of event
        type: string

Jupyter Telemetry uses the ``level`` attribute to drop sensitive data when emitting events. By default, properties greater than "unclassifed" are dropped from recorded event data.

Each logging handler increase the level of sensitive data it emots. This can be configured by changing its ``.event_level`` attribute.

.. code-block:: python

    import logging

    handler = logging.FileHandler('events.log')
    handler.event_level = 'secret'

