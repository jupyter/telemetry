"""
Emit structured, discrete events when various actions happen.
"""
import logging
from datetime import datetime

import jsonschema
try:
    from ruamel.yaml import YAML
except ImportError as e:
    # check for known conda bug that prevents
    # pip from installing ruamel.yaml dependency
    try:
        import ruamel_yaml  # noqa
    except ImportError:
        # nope, regular import error; raise original
        raise e
    else:
        # have conda fork ruamel_yaml, but not ruamel.yaml.
        # this is a bug in the ruamel_yaml conda package
        # mistakenly identifying itself as ruamel.yaml to pip.
        # conda install the 'real' ruamel.yaml to fix
        raise ImportError("Missing dependency ruamel.yaml. Try: `conda install ruamel.yaml`")

from traitlets import (
    List,
    Bool
)
from traitlets.config import Configurable, Config

from .traits import Handlers
from . import TELEMETRY_METADATA_VERSION
from .formatter import JsonEventWithPersonalDataFormatter

yaml = YAML(typ='safe')


class EventLog(Configurable):
    """
    Send structured events to a logging sink
    """
    handlers = Handlers(
        [],
        allow_none=True,
        help="""A list of logging.Handler instances to send events to.

        When set to None (the default), events are discarded.
        """
    ).tag(config=True)

    allowed_schemas = List(
        [],
        help="""
        Fully qualified names of schemas to record.

        Each schema you want to record must be manually specified.
        The default, an empty list, means no events are recorded.
        """
    ).tag(config=True)

    collect_personal_data = Bool(
        False,
        help="""
        If False, no events with personal data will be collected. All events require
        an explicit statement of whether personal data is included.
        """
    )

    allowed_categories = List(
        [],
        help="""
        List of property categories to allow in all recorded events.
        """
    ).tag(config=True)

    def __init__(self, *args, **kwargs):
        # We need to initialize the configurable before
        # adding the logging handlers.
        super().__init__(*args, **kwargs)
        # Use a unique name for the logger so that multiple instances of EventLog do not write
        # to each other's handlers.
        log_name = __name__ + '.' + str(id(self))
        self.log = logging.getLogger(log_name)
        # We don't want events to show up in the default logs
        self.log.propagate = False
        # We will use log.info to emit
        self.log.setLevel(logging.INFO)
        self.schemas = {}
        # Add each handler to the logger and format the handlers.
        if self.handlers:
            for handler in self.handlers:
                handler = self.format_handler(handler)
                self.log.addHandler(handler)

    def format_handler(self, handler):
        """Add a formatter that checks for sensitive data.
        """
        allowed_categories = getattr(
            handler,
            "allowed_categories",
            self.allowed_categories
        )

        # Create a formatter for this handler.
        formatter = JsonEventWithPersonalDataFormatter(
            self,
            allowed_categories
        )
        # Set formatted for handler.
        handler.setFormatter(formatter)
        return handler

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
        required_schema_fields = {'$id', 'version', 'properties', 'personal-data'}
        for rsf in required_schema_fields:
            if rsf not in schema:
                raise ValueError(
                    '{} is required in schema specification'.format(rsf)
                )

        for p, attrs in schema['properties'].items():
            if p.startswith('__'):
                raise ValueError(
                    'Schema {} has properties beginning with __, which is not allowed'
                )

            # Validate "categories" property in proposed schema.
            try:
                cats = attrs['categories']
                # Categories must be a list.
                if not isinstance(cats, list):
                    raise ValueError(
                        'The "categories" field in a registered schemas must be a list.'
                    )

                # Unrestricted is a special case and must be listed alone:
                if 'unrestricted' in cats and len(cats) > 1:
                    raise ValueError(
                        '`unresticted` is a special category. Properties with '
                        '`unrestricted` in their categories list cannot have '
                        'other categories listed too. All `unrestricted` properties '
                        'are emitted when the event is recorded.'
                    )
            except KeyError:
                raise KeyError(
                    'All properties must have a "categories" field that describes '
                    'the type of data being collected. The "{}" property does not '
                    'have a category field.'.format(p)
                )

        self.schemas[(schema['$id'], schema['version'])] = schema

    def record_event(self, schema_name, version, event, timestamp_override=None):
        """
        Record given event with schema has occurred.
        """
        if not (self.handlers and schema_name in self.allowed_schemas):
            # if handler isn't set up or schema is not explicitly whitelisted,
            # don't do anything
            return

        if (schema_name, version) not in self.schemas:
            raise ValueError('Schema {schema_name} version {version} not registered'.format(
                schema_name=schema_name, version=version
            ))
        schema = self.schemas[(schema_name, version)]

        # Only emit the event if personal data is allowed,
        # or personal data is not found in the event.
        if any((
            # If the event contains personal data and personal
            # data is allowed, emit the event.
            schema['personal-data'] and self.collect_personal_data,
            # If the event does not contain personal data,
            # emit the event.
            not schema['personal-data']
        )):
            # Validate the event data.
            jsonschema.validate(event, schema)
            if timestamp_override is None:
                timestamp = datetime.utcnow()
            else:
                timestamp = timestamp_override
            capsule = {
                '__timestamp__': timestamp.isoformat() + 'Z',
                '__schema__': schema_name,
                '__schema_version__': version,
                '__metadata_version__': TELEMETRY_METADATA_VERSION,
            }
            capsule.update(event)
            self.log.info(capsule)
