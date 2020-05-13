from traitlets import HasTraits, validate, Set
from pythonjsonlogger import jsonlogger


class JsonEventFormatter(jsonlogger.JsonFormatter):
    """Patch the jsonlogger formatter to include levels for telemetry.

    Properties in a logged event that has a level less than
    the handler's event_level will be dropped from the emitted event.
    """
    def __init__(self, logger, handler, *args, **kwargs):
        self.logger = logger
        self.handler = handler
        super(JsonEventFormatter, self).__init__(*args, **kwargs)

    @property
    def allowed_tags(self):
        return getattr(self.handler, 'allowed_tags', {})

    @property
    def hashed_tags(self):
        return getattr(self.handler, 'hashed_tags', {})

    def process_log_record(self, log_record):
        log_record = super(JsonEventFormatter, self).process_log_record(log_record)
        return self.process_tags(log_record)

    def drop_property(self, key, record):
        del record[key]
        return record

    def hash_property(self, key, record):
        hash_function = lambda x: x
        record[key] = hash_function(record[key])
        return record

    def process_tags(self, log_record):
        """
        """
        # Registered schemas are identified by their name and version.
        key = (log_record['__schema__'], log_record['__schema_version__'])
        schema = self.logger.schemas[key]['properties']
        props = [key for key in log_record.keys()
                    if not key.startswith('__') and key != 'message']

        # Walk through the recorded event and handle each key
        # based on its tag/category.
        for key in props:
            tag = schema[key]['tag']
            if tag in self.allowed_tags or tag == "unrestricted":
                # If the tag is found in the allowed_tags trait, do nothing.
                if tag in self.hashed_tags:
                    log_record = self.hash_property(key, log_record)
            # Drop tags not listed in allowed_tags
            else:
                log_record = self.drop_property(key, log_record)

        return log_record
