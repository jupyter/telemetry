Writing a schema for telemetry
==============================

All Schemas should be a valid `JSON schema`_ and can be written in valid YAML or JSON.

At a minimum, valid Jupyter Telemetry Event schema requires have the following keys:

- ``$id`` : a URI to identify (and possibly locate) the schema.
- ``version`` : schema version.
- ``title`` : name of the schema
- ``description`` : documentation for the schema
- ``properties`` : attributes of the event being emitted.

    Each property should have the following attributes:

    + ``title`` : name of the property
    + ``description``: documentation for this property.
    + ``categories``: list of types of data being collected

- ``required``: list of required properties.

Here is a minimal example of a valid JSON schema for an event.

.. code-block:: yaml

    $id: event.jupyter.org/example-event
    version: 1
    title: My Event
    description: |
      All events must have a name property
    type: object
    properties:
      thing:
        title: Thing
        categories:
          - category.jupyter.org/unrestricted
        description: A random thing.
      user:
        title: User name
        categories:
          - category.jupyter.org/user-identifier
        description: Name of user who initiated event
    required:
    - thing
    - user


.. _JSON schema: https://json-schema.org/


Property Categories
-------------------

Each property can be labelled with ``categories`` field. This makes it easier to filter properties based on a category. We recommend that schema authors use valid URIs for these labels, e.g. something like ``category.jupyter.org/unrestricted``.

Below is a list of common category labels that Jupyter Telemetry recommends using:

* ``category.jupyter.org/unrestricted``
* ``category.jupyter.org/user-identifier``
* ``category.jupyter.org/user-identifiable-information``
* ``category.jupyter.org/action-timestamp``
