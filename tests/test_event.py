import pytest

from enum import Enum
from pydantic import Schema, ValidationError

from jupyter_telemetry.event import Event


@pytest.fixture
def mock_event():
    # Define a property for MockEvent that's a list.
    class Actions(str, Enum):
        act1 = 'act1'
        act2 = 'act2'

    # Create MockEvent
    class MockEvent(Event):
        _id = 'mock.id'
        _title = 'my mock event'
        _version = 1

        prop1: int = Schema(
            ...,
            title='prop1',
            description="property #1"
        )
        prop2: Actions = Schema(
            ...,
            title='list of actions',
            description="property #2 with list of actions"
        )

    return MockEvent

def test_bad_attr_in_event():
    with pytest.raises(TypeError):
        # Define an event object with the wrong type for "title"
        class MockBadEvent(Event):
            _title = 2
            _version = 1
            _id = 'test'

def test_missing_attr_in_event():
    with pytest.raises(AttributeError):
        # Define an event object with missing attr.
        class MockBadEvent(Event):
            # Missing _version
            _id = 'test'
            _title = 'test'


def test_class_creation():
    # Create a working class
    class MockEvent(Event):
        _id = 'test'
        _title = 'test'
        _version = 1

    assert hasattr(MockEvent, 'Config')
    assert hasattr(MockEvent.Config, 'schema_extra')
    assert all((key in MockEvent.Config.schema_extra for key in ['version', '$id']))


def test_schema_generation():
    # Create a working class
    class MockEvent(Event):
        _id = 'test'
        _title = 'test'
        _version = 1

    schema = MockEvent.schema()
    assert all((key in schema for key in ['title', 'type', '$id', 'version']))


def test_schema_validation(mock_event):
    # Create an instance of mock event.
    # Nothing should happen is validation
    # is successful.
    try:
        event = mock_event(
            prop1=1,
            prop2='act1'
        )
    except:
        pytest.fail("Unexpected error when trying to validate MockEvent instance.")

    data = event.json()
    

def test_schema_validation_failure(mock_event):
    # Setting prop1 to a string raises Validation error.
    with pytest.raises(ValidationError):
        event = mock_event(
            prop1='this is not an int',
            prop2='act1'
        )

