.. _Personal Data:

Personal Data
=============

Jupyter Telemetry does not collect personal data or personally identifiable information (PII) by default. Further, all event schemas registered through the Jupyter Telemetry System must explicitly state whether they collect personal data or not. Operators collecting event data that includes personal data must explicitly opt-in to this feature.

Definition
----------

The following definition comes from Article 4 of the General Data Protection Regulation (GDPR) provided by the European Union:

  * ‘personal data’ means any information relating to an identified or identifiable natural person (‘data subject’); an identifiable natural person is one who can be identified, directly or indirectly, in particular by reference to an identifier such as a name, an identification number, location data, an online identifier or to one or more factors specific to the physical, physiological, genetic, mental, economic, cultural or social identity of that natural person;

Event Schemas with PII
----------------------

Jupyter Telemetry requires all event schemas to define a boolean field, ``personal-data``, that explicitly states whether the event type includes personal data (as defined above). This includes any information that can be considered personally identifiable information. As stated `here <https://gdpr-info.eu/issues/personal-data/>`_:

  Since the [GDPR] definition includes “any information,” one must assume that the term “personal data” should be as broadly interpreted as possible.

Further, Jupyter Telemetry also requires that every property within an event has a ``categories`` field explicitly labeling the type of personal data being collected.

.. code-block:: yaml

    $id: example.schema
    version: 1
    personal-data: true
    properties:
      name:
        title: Name
        categories:
          - unrestricted
        description: Name of event
        type: string
      user:
        title: User name
        categories:
           - personal-identifier
        description: Name of the user who initiated the event.
      affiliation:
        title: Affiliation
        categories:
          - personally-identifiable-information
        description: Affiliation of the user.


Collecting PII
--------------

Jupyter Telemetry does **not** record any personal data by default.

Any events with the field ``personal-data: true`` will not be recorded. Operators must explicitly opt-in to collect personal data by setting the ``EventLog.collect_personal_data`` attribute to ``True``.

.. code-block:: python

    from jupyter_telemetry import EventLog

    e = EventLog(collect_personal_data=True)

This will enable the EventLog to record events with ``personal-data: true``; however, these events will drop all properties that do not have ``category: unrestricted`` (``unrestricted`` is a reserved category for properties that are **always safe** to collect). Properties labeled with other categories will be removed from the event by default.

To record properties with other categories, explicitly list these categories in the ``EventLog.allowed_categories`` attribute.

.. code-block:: python

    from jupyter_telemetry import EventLog

    e = EventLog(
      collect_personal_data=True,
      allowed_categories=['personally-identifiable-information']
    )


The ``categories`` field is a "free field" for schema authors to define. The only special value is ``unrestricted``. The "categories" field requires all schemas to be explicit about the types of data included an logged event capsule, and it ensures that administrators know exactly what type of data they are collecting.