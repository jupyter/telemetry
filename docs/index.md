# Jupyter Telemetry

**Configurable event-logging for Jupyter applications and extensions.**


Telemetry provides a configurable traitlets object, EventLog, for structured event-logging in Python. It leverages Python's standard logging library for filtering, handling, and recording events. All events are validated (using jsonschema) against registered JSON schemas.

The most common way to use Jupyter's telemetry system is to configure the ``EventLog`` objects in Jupyter Applications, (e.g. JupyterLab, Jupyter Notebook, JupyterHub). See the page "[](pages/application.md)".

If you're looking to add telemetry to an application that you're developing, check out the page "[](pages/configure.md)".

If you're looking for client-side telemetry in Jupyter frontend applications (like JupyterLab), checkout the work happening in [jupyterlab-telemetry](https://github.com/jupyterlab/jupyterlab-telemetry)!


## Installation

Jupyter's Telemetry library can be installed from PyPI.

```
pip install jupyter_telemetry
```

## Table of Contents

```{toctree}
:maxdepth: 2

pages/user-guide
```
