import pytest
import logging 
from traitlets import HasTraits, TraitError
from jupyter_telemetry.traits import HandlersList


class HasHandlerList(HasTraits):
    handlers_list = HandlersList(
        None,
        allow_none=True
    )


def test_good_handlers_list_value():
    handlers = [
        logging.NullHandler(), 
        logging.NullHandler()
    ]
    obj = HasHandlerList(
        handlers_list=handlers
    )
    assert obj.handlers_list

def test_bad_handlers_list_values():
    handlers = [0, 1]
    
    with pytest.raises(TraitError):
        obj = HasHandlerList(
            handlers_list=handlers
        )

def test_mixed_handlers_list_values():
    handlers = [
        logging.NullHandler(), 
        1
    ]
    with pytest.raises(TraitError):
        obj = HasHandlerList(
            handlers_list=handlers
        )
