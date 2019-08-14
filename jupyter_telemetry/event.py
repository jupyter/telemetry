from pydantic.main import MetaModel
import pydantic

class MetaEvent(MetaModel):
    """Metaclass that checks for three required class attributes:
        1. _id: the ID of the event
        2. _version: the version of the current schema.
        3. _title: the name of the schema.

    These attribute are mapped to pydantic.BaseModel's `Config` inner class
    for proper schema generation+validation.
    """
    def __new__(cls, name, base, dct):
        # Check that required keys are found.
        if not all((key in dct for key in ['_id', '_title', '_version'])):
            raise AttributeError('Required class attributes are missing from the {} class.'.format(name))

        # Check that keys are the proper types.
        if not all((
            type(dct['_id']) in (str, type(None)),
            type(dct['_version']) in (int, type(None)),
            type(dct['_title']) in (str, type(None))
            )):
            raise TypeError('Check the class attributes types: "_id" must be a string, '
                            '"_version" must be an integer, and "_title" must be a string.')

        # Add a Config inner class to this Pydantic model.
        class Config:
           title = dct['_title']
           schema_extra = {
                '$id': dct['_id'],
                'version': dct['_version']
           }

        dct['Config'] = Config

        return super(MetaEvent, cls).__new__(cls, name, base, dct)


class Event(pydantic.BaseModel, metaclass=MetaEvent):
    """A pydantic Model object for Jupyter Events."""
    _id: str = None
    _version: int = None
    _title: str = None