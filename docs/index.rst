.. telemetry documentation master file, created by
   sphinx-quickstart on Fri Sep 27 16:34:00 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Jupyter Telemetry
=================

**Configurable event-logging for Jupyter applications and extensions.**


Telemetry provides a configurable traitlets object, EventLog, for structured event-logging in Python. It leverages Python's standard logging library for filtering, handling, and recording events. All events are validated (using jsonschema) against registered JSON schemas.

The most common way to use Jupyter's telemetry system is to configure the ``EventLog`` objects in Jupyter Applications, (e.g. JupyterLab, Jupyter Notebook, JupyterHub). See the page ":ref:`using-telemetry`"

If you're looking to add telemetry to an application that you're developing, check out the page ":ref:`adding-telemetry`"

If you're looking for client-side telemetry in Jupyter frontend applications (like JupyterLab), checkout the work happening in jupyterlab-telemetry_!

.. _jupyterlab-telemetry: https://github.com/jupyterlab/jupyterlab-telemetry


Installation
------------

Jupyter's Telemetry library can be installed from PyPI.

.. code-block::

    pip install jupyter_telemetry


.. toctree::
   :maxdepth: 1
   :caption: Table of Contents:

   pages/configure
   pages/application
   pages/schemas

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
