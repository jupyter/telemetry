import logging
from traitlets import TraitType, TraitError, validate


class HandlersList(TraitType):
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
            "Elements in the '{}' trait of an {} instance " \
            "must be Python `logging` handler instances."\
            .format(self.name, obj.__class__.__name__)
        )

    def validate(self, obj, value):
        # If given a list, convert to callable that returns the list.
        if type(value) == list:
            self.validate_elements(obj, value)
            # Wrap list with callable
            def handlers_list(): 
                return value
            return handlers_list
        elif callable(value):
            return value
        else:
            self.error(obj, value)
