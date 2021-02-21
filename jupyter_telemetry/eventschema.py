from collections import deque
from copy import deepcopy

from jsonschema import validators
from jsonschema.exceptions import ValidationError, best_match


class ExtractCategories(ValidationError):
    def __init__(self, property, categories, *args, **kwargs):
        super(ValidationError, self).__init__(*args, **kwargs)
        self.property = property
        self.categories = categories


# Based on https://python-jsonschema.readthedocs.io/en/stable/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance
def extend_with_categories(validator_class):
    """
    Extend the validator class so that during json schema validation, whenever
    the keyword 'categories' is encountered in a valid context with regards to a
    property, it yields an instance of ExtractCategories containing the
    information needed for category filtering later.
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


def categories_and_validation(validator, instance):
    """
    Split the error stream from validator.iter_errors into ValidationError for
    jsonschema validation and ExtractCategories for category filtering
    """
    categories = dict()
    validation_errors = deque()

    for e in validator.iter_errors(instance):
        if isinstance(e, ExtractCategories):
            categories[tuple(e.absolute_path + deque([e.property]))] = e
        else:
            validation_errors.append(e)

    return categories, validation_errors


def raise_best_validation_error(validation_errors):
    error = best_match(validation_errors)
    if error is not None:
        raise error


def filter_categories(
    instance, categories, allowed_categories, allowed_properties, inplace=False
):
    instance = instance if inplace else deepcopy(instance)

    # Top-level properties without declared categories will be given categories []
    for property in instance.keys():
        path = (property,)
        if path not in categories:
            categories[path] = ExtractCategories(property, [], message=None)

    # Allow only properties whose categories are included in allowed_categories
    not_allowed = (
        c for c in categories.values()
        if not set(c.categories).issubset(allowed_categories)
    )

    for c in not_allowed:
        # In case both a sub property and its parent, e.g. ['user', 'name'] and
        # ['user'], do not have all the allowed categories and are to be removed,
        # if the parent is removed first then attempting to remove
        # the descendent would raise either IndexError or KeyError. Just skip it.
        try:
            item = deep_get(instance, c.absolute_path)
        except IndexError:
            continue
        except KeyError:
            continue

        # If a property does not have all the allowed categories, its value is
        # recorded only if it is a top-level property and explicitly listed in
        # allowed_properties. Otherwise record it as null.
        item[c.property] = (
            item[c.property]
            if c.property in allowed_properties and not c.absolute_path
            else None
        )

    return instance


def deep_get(instance, path):
    result = instance
    while path:
        result = result[path.popleft()]
    return result
