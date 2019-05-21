""" JupyterLab LaTex : live Telemetry editing for JupyterLab """

import json
import os
from glob import glob

from tornado import web

from notebook.utils import url_path_join
from notebook.base.handlers import APIHandler, json_errors
from jupyterhub.events import EventLog

from ._version import __version__
here = os.path.dirname(__file__)


class EventLoggingHandler(APIHandler):
    """
    A handler that receives and stores telemetry data from the client.
    """
    @property
    def eventlog(self) -> EventLog:
        return self.settings['eventlog']

    @json_errors
    @web.authenticated
    async def put(self, *args, **kwargs):
        try:
            # Parse the data from the request body
            raw_event = json.loads(self.request.body.strip().decode())
        except Exception as e:
            raise web.HTTPError(400, str(e))
        
        required_fields = {'schema', 'version', 'event'}
        for rf in required_fields:
            if rf not in raw_event:
                raise web.HTTPError(400, f'{rf} is a required field')

        schema_name = raw_event['schema'] 
        version = raw_event['version']
        event = raw_event['event']
        self.eventlog.emit(schema_name, version, event)

        self.set_status(204)
        self.finish()



def _jupyter_server_extension_paths():
    return [{
        'module': 'jupyterlab_telemetry'
    }]

def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app

    eventlog = EventLog(parent=nb_server_app)
    web_app.settings['eventlog'] = eventlog
    for schema_file in glob(os.path.join(here, 'event-schemas','*.json')):
        with open(schema_file) as f:
            eventlog.register_schema(json.load(f))

    # Prepend the base_url so that it works in a jupyterhub setting
    base_url = web_app.settings['base_url']
    endpoint = url_path_join(base_url, 'eventlog')

    handlers = [(endpoint + '(.*)', EventLoggingHandler)]
    web_app.add_handlers('.*$', handlers)