import jsonschema
import fastjsonschema


class EventSchemaValidator:
    def __init__(self, schema):
        pass

    def validate(self, instance):
        pass


class EventSchema:
    def __init__(self, schema, validator_cls: EventSchemaValidator):
        self.schema = schema
        self._validator = validator_cls(schema)

    def validate(self, instance):
        self._validator.validate(instance)


class JSONSchemaError(Exception):
    pass


class JSONValidationError(Exception):
    pass


class JSONSchemaValidator(EventSchemaValidator):
    def __init__(self, schema):
        ivalidator = jsonschema.validators.validator_for(schema)

        try:
            ivalidator.check_schema(schema)
        except jsonschema.SchemaError as e:
            raise JSONSchemaError(e.message) from e

        self._validator = ivalidator(schema)

    def validate(self, instance):
        try:
            self._validator.validate(instance)
        except jsonschema.ValidationError as e:
            raise JSONValidationError(e.message) from e


class FastJSONSchemaValidator(EventSchemaValidator):
    def __init__(self, schema):
        try:
            self._validate = fastjsonschema.compile(schema)
        except fastjsonschema.JsonSchemaDefinitionException as e:
            raise JSONSchemaError(e.message) from e
        except Exception as e:
            raise JSONSchemaError from e

    def validate(self, instance):
        try:
            self._validate(instance)
        except fastjsonschema.JsonSchemaException as e:
            raise JSONValidationError(e.message) from e


JSON_SCHEMA_VALIDATORS = {
    'jsonschema': JSONSchemaValidator,
    'fastjsonschema': FastJSONSchemaValidator
}
