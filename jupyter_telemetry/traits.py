import logging

from traitlets import TraitType, TraitError


class Handlers(TraitType):
    """A trait that takes a list of logging handlers and converts
    it to a callable that returns that list (thus, making this
    trait pickleable).
    """
    info_text = "a list of logging handlers"

    def validate_elements(self, obj, value):
        if len(value) > 0:
            # Check that all elements are logging handlers.
            for el in value:
                if isinstance(el, logging.Handler) is False:
                    self.element_error(obj)

    def element_error(self, obj):
        raise TraitError(
            "Elements in the '{}' trait of an {} instance "
            "must be Python `logging` handler instances."
            .format(self.name, obj.__class__.__name__)
        )

    def validate(self, obj, value):
        # If given a callable, call it and set the
        # value of this trait to the returned list.
        # Verify that the callable returns a list
        # of logging handler instances.
        if callable(value):
            out = value()
            self.validate_elements(obj, out)
            return out
        # If a list, check it's elements to verify
        # that each element is a logging handler instance.
        elif type(value) == list:
            self.validate_elements(obj, value)
            return value
        else:
            self.error(obj, value)


class SchemaOptions(TraitType):
    """A trait for handling options for recording schemas.
    """
    info_text = "either a dictionary with schema options or a list with schema names."

    def validate(self, obj, val):
        # If the type is a dictionary.
        if type(val) is dict:
            for schema_name, data in val.items():
                given_keys = set(data.keys())
                # Compare against keys expected.
                allowed_keys = {"categories", "properties"}
                # There should be no extra keys (anything other than
                # allowed_keys) in the schema options.
                unknown_keys = given_keys.difference(allowed_keys)
                if unknown_keys:
                    # Throw an error if there are unknown keys.
                    raise TraitError(
                        "The schema option, {schema_name}, includes "
                        "unknown key(s): {unknown_keys}".format(
                           schema_name=schema_name,
                           unknown_keys=",".join(unknown_keys)
                        )
                    )
            validated_val = val
        # If the type is a list (for backwards compatibility).
        elif type(val) is list:
            validated_val = {}
            for schema_name in val:
                validated_val[schema_name] = {}
        else:
            raise TraitError("SchemaOptions must be of type dict or list.")
        return validated_val
