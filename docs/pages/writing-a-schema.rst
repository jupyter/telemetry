Writing a Schema
================


Schemas should follow valid `JSON schema`_. These schemas can be written in valid YAML or JSON.

At a minimum, valid schemas should have the following keys:

- ``$id`` : a valid URL where the schema lives.
- ``version`` : schema version.
- ``title`` : name of the schema
- ``description`` : documentation for the schema
- ``properties`` : attributes of the event being emitted.

    Each property should have the following attributes:

    + ``title`` : name of the property
    + ``description``: documentation for this property.
    + ``pii``: (optional) boolean for whether this property is personally identifiable information or not.

- ``required``: list of required properties.

Here is a minimal example of a valid JSON schema for an event.

.. code-block:: yaml

    $id: url.to.event.schema
    version: 1
    title: My Event
    description: |
      All events must have a name property
    type: object
    properties:
      name:
        title: Name
        description: |
            Name of event
        type: string
    required:
    - name


.. _JSON schema: https://json-schema.org/