from collections import deque

from jsonschema import Draft7Validator, validators
from jsonschema.exceptions import ValidationError


class ExtractCategories(ValidationError):
    """
    A special `jsonschema.ValidationError` that carries information about the
    `categories` keyword, intended to be yielded whenever a `categories` keyword
    is encountered during `jsonschema` JSON validation.

    The primary use case for this class is to make use of the JSON validation
    mechanism implemented by `jsonschema` to extract all categories associated
    with each property in a JSON instance based on a JSON schema. It is not
    intended to be used as an actual validation error.
    """

    def __init__(self, property, categories, *args, **kwargs):
        super(ValidationError, self).__init__(*args, **kwargs)
        self.property = property
        self.categories = categories


def extend_with_categories(validator_class):
    """
    Extend a `jsonschema.IValidator` class so that it yields a `_ExtractCategories`
    whenever a `categories` keyword is encountered during JSON validation

    Parameters
    ----------
    validator_class : jsonschema.IValidator
        an existing validator class

    Returns
    -------
    jsonschema.IValidator
        a new `jsonschema.IValidator` class extending the one provided

    Examples
    --------
    from jsonschema import Draft7Validator


    CategoryExtractor = extend_with_categories(Draft7Validator)
    """
    validate_properties = validator_class.VALIDATORS["properties"]

    def get_categories(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "categories" in subschema:
                yield ExtractCategories(property, subschema["categories"], message=None)

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties": get_categories},
    )


JSONSchemaValidator = Draft7Validator
CategoryExtractor = extend_with_categories(JSONSchemaValidator)


# Ignore categories under any of these jsonschema keywords
IGNORE_CATEGORIES_SCHEMA_KEYWORDS = {
    'if', 'not', 'anyOf', 'oneOf', 'then', 'else'
}


def extract_categories_from_errors(errors):
    for e in errors:
        if (
            isinstance(e, ExtractCategories) and
            not any(p in IGNORE_CATEGORIES_SCHEMA_KEYWORDS
                    for p in e.absolute_schema_path)
        ):
            yield e
        else:
            yield from extract_categories_from_errors(e.context)


def extract_categories_from_event(event, schema):
    """
    Generate a `dict` of `_ExtractCategories` whose keys are pointers to the properties

    Parameters
    ----------
    event : dict
        A telemetry event

    schema : dict
        A JSON schema

    Returns
    -------
    dict
        A mapping from properties in the event to their categories.

        In each entry, the key is a pointer to a property in the event
        (in the form of a tuple) and the value is a `_ExtractCategories`
        containing the categories associated with that property.
    """
    return {
        tuple(c.absolute_path + deque([c.property])): c
        for c in extract_categories_from_errors(
            CategoryExtractor(schema).iter_errors(event)
        )
    }


def filter_categories_from_event(event, schema, allowed_categories, allowed_properties):
    """
    Filter properties from an event based on their categories.

    Only whitelisted properties and properties whose categories are allowed are kept.

    Parameters
    ----------
    event : dict
        The input telemetry event

    schema : dict
        A JSON schema that makes use of the the `categories` keyword to
        specify what categories are associated with a certain property.

    allowed_categories : set
        Specify which categories are allowed

    allowed_properties : set
        Whitelist certain top level properties.

        These properties are included in the output event even if not all of
        their properties are allowed.

    Returns
    -------
    dict
        The output event after category filtering

    """
    categories = extract_categories_from_event(event, schema)

    # Top-level properties without declared categories are set to null
    for property in event.keys():
        path = (property,)
        if path not in categories:
            event[property] = None

    # Allow only properties whose categories are included in allowed_categories
    # and whose top-level parent is included in allowed_properties
    not_allowed = (
        c for p, c in categories.items()
        if not (set(c.categories).issubset(allowed_categories) or
                p[0] in allowed_properties)
    )

    for c in not_allowed:
        # In case both a sub property and its parent, e.g. ['user', 'name'] and
        # ['user'], do not have all the allowed categories and are to be removed,
        # if the parent is removed first then attempting to access
        # the descendent would either return None or raise an IndexError or
        # KeyError. Just skip it.
        try:
            item = deep_get(event, c.absolute_path)
        except IndexError:
            continue
        except KeyError:
            continue

        if item is not None:
            item[c.property] = None

    return event


def deep_get(instance, path):
    result = instance
    while result is not None and path:
        result = result[path.popleft()]
    return result
