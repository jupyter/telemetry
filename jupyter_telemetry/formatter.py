from traitlets import HasTraits, validate, Set
from pythonjsonlogger import jsonlogger


class JsonEventWithPersonalDataFormatter(jsonlogger.JsonFormatter):
    """Patch the jsonlogger formatter to include levels for telemetry.

    Properties in a logged event that has a level less than
    the handler's event_level will be dropped from the emitted event.
    """
    def __init__(
        self,
        logger,
        allowed_categories,
        *args,
        **kwargs
    ):
        self.logger = logger
        self.allowed_categories = allowed_categories
        super(JsonEventWithPersonalDataFormatter, self).__init__(*args, **kwargs)

    def process_log_record(self, log_record):
        # Use the parent process_log_record
        log_record = super(
            JsonEventWithPersonalDataFormatter,
            self
        ).process_log_record(log_record)
        # Remove 'message' from log record.
        # It is always emitted with 'null', and we do not want it,
        # since we are always emitting events only
        del log_record['message']
        # Redact sensitive information.
        return self.handle_category(log_record)

    def handle_category(self, log_record):
        """Looks at the event schema's category for personal data.
        If personal data is present, record event only if category is allowed.
        """

        # Registered schemas are identified by their name and version.
        key = (
            log_record['__schema__'],
            log_record['__schema_version__'],
        )
        schema = self.logger.schemas[key]

        # Pull out the properties from the log_record.
        props = [key for key in log_record if not key.startswith('__')]

        # Walk through the recorded event and handle each key
        # based on its tag/category.
        for key in props:
            category = schema['properties'][key]['category']
            # Allow properties tagged with a whitelisted category.
            if category in self.allowed_categories + ['unrestricted']:
                continue
            # Delete any other property
            else:
                del log_record[key]

        return log_record
