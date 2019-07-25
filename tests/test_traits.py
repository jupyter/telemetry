import logging

import pytest
from traitlets import HasTraits, TraitError

from jupyter_telemetry.traits import Handlers


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
