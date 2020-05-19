Personal Data
=============

Jupyter Telemtry does not collect personal data by default. Further, all event schemas registered through the Jupyter Telemtry system must explicitly state whether they collect personal data or not. Operators that want to record event data that include personal data must explicitly opt-in to this feature.

Definition
----------

The following definition comes from Article 4 of the General Data Protection Regulation (GDPR) provided by the European Union:

  ‘personal data’ means any information relating to an identified or identifiable natural person (‘data subject’); an identifiable natural person is one who can be identified, directly or indirectly, in particular by reference to an identifier such as a name, an identification number, location data, an online identifier or to one or more factors specific to the physical, physiological, genetic, mental, economic, cultural or social identity of that natural person;

Personal data in events
-----------------------

Jupyter telemetry requires all event schemas to define a boolean field, ``personal-data``, that explicitly states whether the event type includes personal data (as defined above). This includes any information that can be considered personally identifiable information. As stated `here <https://gdpr-info.eu/issues/personal-data/>`_:

  Since the [GDPR] definition includes “any information,” one must assume that the term “personal data” should be as broadly interpreted as possible.

Further, Jupyter Telemetry also requires that every property within an event has a ``category`` field explicitly labeling the type of personal data being collected.

.. code-block:: yaml

    $id: example.schema
    version: 1
    personal-data: true
    properties:
      name:
        title: Name
        category: unrestricted
        description: Name of event
        type: string
      user:
        title: User name
        category: personal-identifier
        description: Name of the user who initiated the event.
      affiliation:
        title: Affilition
        category: personally-identifiable-information
        description: Affiliation of the user.

Collecting personal data
------------------------

As mentioned above, Jupyter telemetry dpes **not** record any personal data by default. Operators must explicitly opt-in to collect personal data by setting the ``EventLog``'s ``collect_personal_data`` attribute to True.

.. code-block:: python

    from jupyter_telemetry import EventLog

    e = EventLog(collect_personal_data=True)
