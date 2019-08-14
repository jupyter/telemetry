"""
Emit structured, discrete events when various actions happen.
"""
import json
import logging
from datetime import datetime

import jsonschema
import pydantic

from pythonjsonlogger import jsonlogger
from ruamel.yaml import YAML
from traitlets import List
from traitlets.config import Configurable, Config

from .traits import Handlers


yaml = YAML(typ='safe')


def _skip_message(record, **kwargs):
    """
    Remove 'message' from log record.

    It is always emitted with 'null', and we do not want it,
    since we are always emitting events only
    """
    del record['message']
    return json.dumps(record, **kwargs)


class EventLog(Configurable):
    """
    Send structured events to a logging sink
    """
    handlers = Handlers(
        [],
        config=True,
        allow_none=True,
        help="""A list of logging.Handler instances to send events to.

        When set to None (the default), events are discarded.
        """
    )

    allowed_schemas = List(
        [],
        config=True,
        help="""
        Fully qualified names of schemas to record.

        Each schema you want to record must be manually specified.
        The default, an empty list, means no events are recorded.
        """
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = logging.getLogger(__name__)
        # We don't want events to show up in the default logs
        self.log.propagate = False
        # We will use log.info to emit
        self.log.setLevel(logging.INFO)

        if self.handlers:
            formatter = jsonlogger.JsonFormatter(json_serializer=_skip_message)
            for handler in self.handlers:
                handler.setFormatter(formatter)
                self.log.addHandler(handler)

        self.schemas = {}

    def _load_config(self, cfg, section_names=None, traits=None):
        """Load EventLog traits from a Config object, patching the
        handlers trait in the Config object to avoid deepcopy errors.

        """
        my_cfg = self._find_my_config(cfg)
        handlers = my_cfg.pop("handlers", [])

        # Turn handlers list into a pickeable function
        def get_handlers():
            return handlers

        my_cfg["handlers"] = get_handlers

        # Build a new eventlog config object.
        eventlog_cfg = Config({"EventLog": my_cfg})
        super(EventLog, self)._load_config(eventlog_cfg, section_names=None, traits=None)

    def register_schema_file(self, filename):
        """
        Convenience function for registering a JSON schema from a filepath

        Supports both JSON & YAML files.
        """
        # Just use YAML loader for everything, since all valid JSON is valid YAML
        with open(filename) as f:
            self.register_schema(yaml.load(f))

    def register_schema(self, schema):
        """
        Register a given JSON Schema with this event emitter

        'version' and '$id' are required fields.
        """
        # Check if our schema itself is valid
        # This throws an exception if it isn't valid
        jsonschema.validators.validator_for(schema).check_schema(schema)

        # Check that the properties we require are present
        required_schema_fields = {'$id', 'version'}
        for rsf in required_schema_fields:
            if rsf not in schema:
                raise ValueError(
                    '{} is required in schema specification'.format(rsf)
                )

        # Make sure reserved, auto-added fields are not in schema
        if any([p.startswith('__') for p in schema['properties']]):
            raise ValueError(
                'Schema {} has properties beginning with __, which is not allowed'
            )

        self.schemas[(schema['$id'], schema['version'])] = schema

    def register_events(self, events):
        """Register schemas from pydantic Model objects.

        events : list of pydantic Model objects.
        """
        for event in events:
            print(event)
            if not issubclass(event, pydantic.BaseModel):
                raise TypeError("event must be a subclass of pydantic.BaseModel.")
            self.register_schema(event.schema())

    def record_event(self, event):
        """
        Record given event with schema has occurred.

        event: dict or pydantic object.
            If dict, validates the 
        """
        # Validate if event is raw JSON
        validate = True

        # If event is a pydantic object, it will alreaby be validated.
        if issubclass(event.__class__, pydantic.BaseModel):
            # Get extra args from schema
            version = event.Config.schema_extra['version']
            schema_name = event.Config.schema_extra['$id']
            # Get Event data as dict (ugly hack)
            capsule = json.loads(event.json())
            validate = False
        else:
            version = event.pop('version')
            schema_name = event.pop('$id')
            capsule = event

        if not (self.handlers and schema_name in self.allowed_schemas):
            # if handler isn't set up or schema is not explicitly whitelisted,
            # don't do anything
            return

        if (schema_name, version) not in self.schemas:
            raise ValueError('Schema {schema_name} version {version} not registered'.format(
                schema_name=schema_name, version=version
            ))
        schema = self.schemas[(schema_name, version)]
        
        # Validate raw JSON with jsonschema.
        if validate:
            jsonschema.validate(event, schema)
            capsule = event

        capsule.update({
            '__timestamp__': datetime.utcnow().isoformat() + 'Z',
            '__schema__': schema_name,
            '__version__': version
        })
        self.log.info(capsule)
