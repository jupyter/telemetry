import pytest

from .utils import run_event_test


SCHEMA_ID = 'test.event'
VERSION = 1


NESTED_CATEGORY_SCHEMA = {
    '$id': SCHEMA_ID,
    'title': 'Test Event',
    'version': VERSION,
    'description': 'Test Event.',
    'type': 'object',
    'properties': {
        'nothing-exciting': {
            'description': 'a property with nothing exciting happening',
            'categories': ['unrestricted'],
            'type': 'string'
        },
        'user': {
            'description': 'user',
            'categories': ['user-identifier'],
            'type': 'object',
            'properties': {
                'email': {
                    'description': 'email address',
                    'categories': ['user-identifiable-information'],
                    'type': 'string'
                },
                'id': {
                    'description': 'user ID',
                    'type': 'string'
                }
            }
        }
    }
}


NESTED_EVENT_DATA = {
    'nothing-exciting': 'hello, world',
    'user': {
        'id': 'test id',
        'email': 'test@testemail.com',
    }
}


@pytest.mark.parametrize(
    'allowed_schemas,expected_output',
    [
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': []}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': None
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': ['unrestricted']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': None
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': ['user-identifier']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': {
                    'id': 'test id',
                    'email': None
                }
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': ['user-identifiable-information']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': None
            }
        ),
        (
            # User configuration for allowed_schemas
            {
                SCHEMA_ID: {
                    'allowed_categories': [
                        'user-identifier',
                        'user-identifiable-information'
                    ]
                }
            },
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': {
                    'id': 'test id',
                    'email': 'test@testemail.com',
                }
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_properties': ['user']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'user': {
                    'id': 'test id',
                    'email': 'test@testemail.com',
                }
            }
        ),
    ]
)
def test_category_filtering(allowed_schemas, expected_output):
    run_event_test(
        NESTED_EVENT_DATA,
        NESTED_CATEGORY_SCHEMA,
        SCHEMA_ID,
        VERSION,
        allowed_schemas,
        expected_output
    )


NESTED_CATEGORY_ARRAY_SCHEMA = {
    '$id': SCHEMA_ID,
    'title': 'Test Event',
    'version': VERSION,
    'description': 'Test Event.',
    'type': 'object',
    'properties': {
        'nothing-exciting': {
            'description': 'a property with nothing exciting happening',
            'categories': ['unrestricted'],
            'type': 'string'
        },
        'users': {
            'description': 'user',
            'categories': ['user-identifier'],
            'type': 'array',
            'items': {
                'properties': {
                    'email': {
                        'description': 'email address',
                        'categories': ['user-identifiable-information'],
                        'type': 'string'
                    },
                    'id': {
                        'description': 'user ID',
                        'type': 'string'
                    }
                }
            }
        }
    }
}


ARRAY_EVENT_DATA = {
    'nothing-exciting': 'hello, world',
    'users': [
        {
            'id': 'test id 0',
            'email': 'test0@testemail.com',
        },
        {
            'id': 'test id 1',
            'email': 'test1@testemail.com',
        }
    ]
}


@pytest.mark.parametrize(
    'allowed_schemas,expected_output',
    [
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': []}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'users': None
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': ['unrestricted']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'users': None
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': ['user-identifier']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'users': [
                    {
                        'id': 'test id 0',
                        'email': None,
                    },
                    {
                        'id': 'test id 1',
                        'email': None,
                    }
                ]
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_categories': ['user-identifiable-information']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'users': None
            }
        ),
        (
            # User configuration for allowed_schemas
            {
                SCHEMA_ID: {
                    'allowed_categories': [
                        'user-identifier',
                        'user-identifiable-information'
                    ]
                }
            },
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'users': [
                    {
                        'id': 'test id 0',
                        'email': 'test0@testemail.com',
                    },
                    {
                        'id': 'test id 1',
                        'email': 'test1@testemail.com',
                    }
                ]
            }
        ),
        (
            # User configuration for allowed_schemas
            {SCHEMA_ID: {'allowed_properties': ['users']}},
            # Expected properties in the recorded event
            {
                'nothing-exciting': 'hello, world',
                'users': [
                    {
                        'id': 'test id 0',
                        'email': 'test0@testemail.com',
                    },
                    {
                        'id': 'test id 1',
                        'email': 'test1@testemail.com',
                    }
                ]
            }
        ),
    ]
)
def test_array_category_filtering(allowed_schemas, expected_output):
    run_event_test(
        ARRAY_EVENT_DATA,
        NESTED_CATEGORY_ARRAY_SCHEMA,
        SCHEMA_ID,
        VERSION,
        allowed_schemas,
        expected_output
    )
