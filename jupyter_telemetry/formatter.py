from pythonjsonlogger import jsonlogger


EVENT_MAP = {
    'unrestricted': 0,
    'user-identifier': 10,
    'user-identifiable-information': 20
}

EVENT_LEVELS = list(EVENT_MAP.keys())


class JsonEventFormatter(jsonlogger.JsonFormatter):
    """Patch the jsonlogger formatter to include levels for telemetry.

    Properties in a logged event that has a level less than
    the handler's event_level will be dropped from the emitted event.
    """

    def __init__(self, logger, handler, *args, **kwargs):
        self.logger = logger
        self.handler = handler
        # Set the event logging level
        self.event_level = getattr(handler, 'event_level', None)
        super(JsonEventFormatter, self).__init__(*args, **kwargs)

    # Protect the event_level attribute.
    @property
    def event_level(self):
        """Event Log security level."""
        return self._event_level

    @event_level.setter
    def event_level(self, event_level):
        # Check that the event level makes sense.
        if event_level not in EVENT_LEVELS:
            raise Exception("Event level '{}' not understood.".format(event_level))
        self._event_level = self.handler.event_level

    def process_log_record(self, log_record):
        log_record = super(JsonEventFormatter, self).process_log_record(log_record)
        return self.process_event_levels(log_record)

    def process_event_levels(self, log_record):
        """Removes any properties in a log_record that have an attribute `pii = True`.
        """
        # Get schema for this log_record
        key = (log_record['__schema__'], log_record['__version__'])
        schema = self.logger.schemas[key]['properties']

        # Find all properties that have a level less than the handler.
        keys = list(log_record.keys())
        for key in keys:
            # Ignore any keys that start with __
            if not key.startswith('__'):
                # Check if security level is listed in the schema.
                if EVENT_MAP[schema[key]['level']] > EVENT_MAP[self.event_level]:
                    # If property's level is less than handler's level,
                    # delete this property from the log record.
                    del log_record[key]

        return log_record
