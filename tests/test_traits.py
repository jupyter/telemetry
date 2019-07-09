import pytest

import logging 

from traitlets import HasTraits
from traitlets.tests.test_traitlets import TraitTestBase
from jupyter_telemetry.traits import HandlersList


class HandlersListTrait(HasTraits):
    
    value = HandlersList(
        None,
        allow_none=True
    )


class TestHandlersList(TraitTestBase):

    obj = HandlersListTrait()

    _default_value = None
    _good_values = [
        [logging.NullHandler(), logging.NullHandler()]
    ]
    _bad_values = [
        [0, 1],
        ['a', 'b'],
        [logging.NullHandler(), 0]
    ]

    def assertEqual(self, a, b):
        # Hijack assertEquals method to check for comparison between two callables
        if callable(a) and callable(b):
            pass
        else:
            super(TestHandlersList, self).assertEqual(a, b)

    def coerce(self, value):
        # Coerce value when comparing the trait's value to
        # the given value.
        def handlers_list():
            return value
        return handlers_list