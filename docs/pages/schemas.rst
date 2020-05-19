Writing a Schema
================

All Schemas should be a valid `JSON schema`_ and can be written in valid YAML or JSON.

At a minimum, valid Jupyter Telemetry Event schema requires have the following keys:

- ``$id`` : a valid URL where the schema lives.
- ``version`` : schema version.
- ``title`` : name of the schema
- ``description`` : documentation for the schema
- ``personal-data``: boolean explicitly stating if personal data is collected.
- ``properties`` : attributes of the event being emitted.

    Each property should have the following attributes:

    + ``title`` : name of the property
    + ``description``: documentation for this property.
    + ``category``: type of data being collected

- ``required``: list of required properties.

Here is a minimal example of a valid JSON schema for an event.

.. code-block:: yaml

    $id: url.to.event.schema
    version: 1
    title: My Event
    personal-data: true
    description: |
      All events must have a name property
    type: object
    properties:
      thing:
        title: Thing
        category: unrestricted
        description: A random thing.
      user:
        title: User name
        catergory: user-identifier
        description: Name of user who initiated event
    required:
    - thing
    - user


.. _JSON schema: https://json-schema.org/

It is important that every schema explicity state whether it collects personal-data or not. See the :ref:`Personal Data` page for more information.