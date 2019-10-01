from pythonjsonlogger import jsonlogger

EVENT_LEVELS = [
    'unclassified',
    'confidential',
    'secret',
    'top_secret'
]

EVENT_MAP = {
    'unclassified': 0,
    'confidential': 10,
    'secret': 20,
    'top_secret': 30
}


class JsonEventFormatter(jsonlogger.JsonFormatter):
    """Patch the jsonlogger formatter to include levels for telemetry.

    Properties in a logged event that has a level less than
    the handler's event_level will be dropped from the emitted event.
    """

    def __init__(self, logger, handler, *args, **kwargs):
        self.logger = logger
        self.handler = handler

        # Set the event logging level
        if hasattr(self.handler, 'event_level'):
            event_level = self.handler.event_level 
        else:
            event_level = 'unclassified' 
        self.setEventLevel(event_level)

        super(JsonEventFormatter, self).__init__(*args, **kwargs)

    def setEventLevel(self, event_level):
        # Check that the event level makes sense.
        if event_level not in EVENT_LEVELS:
            raise Exception("Event level '{}' not understood.".format(event_level))
        self._event_level = self.handler.event_level

    # Protect the event_level attribute.
    @property
    def event_level(self):
        """Event Log security level."""
        return self._event_level

    def process_log_record(self, log_record):
        log_record = super(JsonEventFormatter, self).process_log_record(log_record)
        return self.process_event_levels(log_record)
        
    def process_event_levels(self, log_record):
        """Removes any properties in a log_record that have an attribute `pii = True`.
        """
        # Get schema for this log_record
        key = (log_record['__schema__'], log_record['__version__'])
        schema = self.logger.schemas[key]['properties']
    
        # Logging keys that won't be in the schema.
        ignored_keys = ['__schema__', '__timestamp__', '__version__', 'message']

        # Find all properties that have a level less than the handler.
        keys = list(log_record.keys())
        for key in keys:
            if key not in ignored_keys:
                # Check if PII is listed in the schema.
                if EVENT_MAP[schema[key]['level']] > EVENT_MAP[self.event_level]:
                    # If property's level is less than handler's level, 
                    # delete this property from the log record.
                    del log_record[key]
        
        return log_record