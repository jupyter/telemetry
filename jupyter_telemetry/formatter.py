from pythonjsonlogger import jsonlogger


class JsonEventFormatter(jsonlogger.JsonFormatter):
    """A subclass of pythonjsonlogger's log formatter for handling
    telemetry data. Adds a formatter to logging handlers that
    dr
    """

    def __init__(self, logger, handler, *args, **kwargs):
        self.logger = logger
        self.handler = handler

        # Should this formatter allow PII?
        if hasattr(self.handler, 'include_pii'):
            self.include_pii = self.handler.include_pii
        else:
            self.include_pii

        super(JsonEventFormatter, self).__init__(*args, **kwargs)

    def process_log_record(self, log_record):
        log_record = super(JsonEventFormatter, self).process_log_record(log_record)
        return self.drop_personally_identifiable_information(log_record)
        
    def drop_personally_identifiable_information(self, log_record):
        """Removes any properties in a log_record that have an attribute `pii = True`.
        """
        # If the handler does not allow PII info through, remove it.
        if not self.include_pii:

            # Get schema for this log_record
            key = (log_record['__schema__'], log_record['__version__'])
            schema = self.logger.schemas[key]['properties']
        
            # Logging keys that won't be in the schema.
            ignored_keys = ['__schema__', '__timestamp__', '__version__', 'message']

            keys = list(log_record.keys())
            for key in keys:
                if key not in ignored_keys:
                    # Check if PII is listed in the schema.
                    if 'pii' in schema[key]:
                        # If property is PII and handler doesn't allow_pii, 
                        # delete this property from the log record.
                        if schema[key]['pii']:
                            del log_record[key]
        
        return log_record