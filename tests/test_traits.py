import logging

import pytest
from traitlets import HasTraits, TraitError

from jupyter_telemetry.traits import Handlers, SchemaOptions


class HasHandlers(HasTraits):
    handlers = Handlers(
        None,
        allow_none=True
    )


def test_good_handlers_value():
    handlers = [
        logging.NullHandler(),
        logging.NullHandler()
    ]
    obj = HasHandlers(
        handlers=handlers
    )
    assert obj.handlers == handlers


def test_bad_handlers_values():
    handlers = [0, 1]

    with pytest.raises(TraitError):
        HasHandlers(
            handlers=handlers
        )


def test_mixed_handlers_values():
    handlers = [
        logging.NullHandler(),
        1
    ]
    with pytest.raises(TraitError):
        HasHandlers(
            handlers=handlers
        )


class HasSchemaOptions(HasTraits):
    schema_options = SchemaOptions({}, allow_none=True)


@pytest.mark.parametrize(
    "schema_options",
    [
        # schema_options can be a list of schema_names. In this case,
        # the SchemaOptions trait will turn this list into a dictionary
        # with the list items as keys the values as empty dictionaries.
        ["schema_name_1", "schema_name_2"],
        # Empty nested config are okay.
        {"schema_name_1": {}},
        # Nested config with empty values is okay too.
        {"schema_name_1": {"allowed_categories": []}},
        # Test complete config for good measure.
        {"schema_name_1": {"allowed_categories": ["value"]}},
        # Test multiple values.
        {"schema_name_1": {"allowed_categories": ["value"]}, "schema_name_2": {}},
    ]
)
def test_good_schema_options(schema_options):
    obj = HasSchemaOptions(schema_options=schema_options)
    assert type(obj.schema_options) == dict


@pytest.mark.parametrize(
    "schema_options",
    [
        # Raise an error if Schema Options has unknown attribute.
        {"schema_name_1": {"unknown_attribute": []}},
        # Test multiple values.
        {
            "schema_name_1": {
                "allowed_categories": ["value"]
            },
            "schema_name_2": {
                "unknown_attribute": []
            }
        },
    ]
)
def test_bad_schema_options(schema_options):
    with pytest.raises(TraitError):
        HasSchemaOptions(schema_options=schema_options)