from pydantic.main import MetaModel
import pydantic

class MetaEvent(MetaModel):
    """Metaclass that maps required ar"""
    def __new__(cls, name, base, dct):

        class Config:
           title = dct['_title']
           schema_extra = {
                '$id': dct['_id'],
                'version': dct['_version']
           }

        dct['Config'] = Config

        return super(MetaEvent, cls).__new__(cls, name, base, dct)


Event = MetaEvent('Event', (pydantic.BaseModel,), {'_id': None, '_version': None, '_title': None})