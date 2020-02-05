Schema Documentation in Sphinx
==============================

Jupyter Telemetry provides a Sphinx Extension to automatically generate documentation
from a directory of Event-logging schemas.

To activate this extension, add ``jupyter_telemetry.sphinxext`` to your ``conf.py`` file
and set the following configuration values:

.. code-block:: python

    # config.py file.

    extensions = [
        'jupyter_telemetry.sphinxext',
        ...
    ]

    # Jupyter telemetry configuration values.
    jupyter_telemetry_schema_source = "path/to/schemas/source/directory"   # Path is relative to conf.py
    jupyter_telemetry_schema_output = "path/to/output/directory"           # Path is relative to conf.py
    jupyter_telemetry_index_title = "Example Event Schemas"                # Title of the index page that lists all found schemas.


