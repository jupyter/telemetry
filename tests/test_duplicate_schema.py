from jupyter_telemetry.eventlog import EventLog

import pytest
from ruamel.yaml import YAML


SCHEMA_1 = {
    '$id': 'test/test',
    'version': 1,
    'properties': {
        'something': {
            'type': 'string',
            'categories': ['unrestricted']
        },
    },
}


# same $id different versions
SCHEMA_2 = {
    '$id': 'test/test',
    'version': 2,
    'properties': {
        'somethingelse': {
            'type': 'string',
            'categories': ['unrestricted']
        },
    },
}


# same $id same version different properties
SCHEMA_3 = {
    '$id': 'test/test',
    'version': 1,
    'properties': {
        'somethingelse': {
            'type': 'string',
            'categories': ['unrestricted']
        },
    },
}


def create_schema_files(tmp_path, schemas):
    yaml = YAML(typ='safe')

    schema_files = [
        (schema, tmp_path / f'schema{i}.yml')
        for i, schema in enumerate(schemas)
    ]

    for schema, f in schema_files:
        yaml.dump(schema, f)

    return schema_files


def test_skip_duplicate_schema(tmp_path):
    (schema_1, file_1), (schema_2, file_2) = (
        create_schema_files(tmp_path, (SCHEMA_1, SCHEMA_2))
    )

    el = EventLog()

    el.register_schema_file(file_1)
    el.register_schema_file(file_2, duplicate='skip')

    assert (schema_1['$id'], schema_1['version']) in el.schemas.keys()
    assert (schema_2['$id'], schema_2['version']) not in el.schemas.keys()

    expected = el.schemas[(schema_1['$id'], schema_1['version'])]
    assert schema_1.items() <= expected.items()


def test_allow_duplicate_schema_same_version(tmp_path):
    (schema_1, file_1), (schema_2, file_2) = (
        create_schema_files(tmp_path, (SCHEMA_1, SCHEMA_3))
    )

    el = EventLog()

    el.register_schema_file(file_1)
    el.register_schema_file(file_2, duplicate='allow')

    assert (schema_1['$id'], schema_1['version']) in el.schemas.keys()
    assert (schema_2['$id'], schema_2['version']) in el.schemas.keys()

    notexpected = el.schemas[(schema_1['$id'], schema_1['version'])]
    assert not schema_1.items() <= notexpected.items()

    expected = el.schemas[(schema_2['$id'], schema_2['version'])]
    assert schema_2.items() <= expected.items()


def test_allow_duplicate_schema_different_versions(tmp_path):
    (schema_1, file_1), (schema_2, file_2) = (
        create_schema_files(tmp_path, (SCHEMA_1, SCHEMA_2))
    )

    el = EventLog()

    el.register_schema_file(file_1)
    el.register_schema_file(file_2, duplicate='allow')

    assert (schema_1['$id'], schema_1['version']) in el.schemas.keys()
    assert (schema_2['$id'], schema_2['version']) in el.schemas.keys()

    expected = el.schemas[(schema_1['$id'], schema_1['version'])]
    assert schema_1.items() <= expected.items()

    expected = el.schemas[(schema_2['$id'], schema_2['version'])]
    assert schema_2.items() <= expected.items()


def test_raise_duplicate_schema(tmp_path):
    (schema_1, file_1), (schema_2, file_2) = (
        create_schema_files(tmp_path, (SCHEMA_1, SCHEMA_2))
    )

    el = EventLog()

    el.register_schema_file(file_1)
    with pytest.raises(ValueError):
        el.register_schema_file(file_2, duplicate='raise')


def test_default_duplicate_schema(tmp_path):
    test_raise_duplicate_schema(tmp_path)


# test invalid `duplicate` value
def test_invalid_duplicate_schema(tmp_path):
    (schema_1, file_1), (schema_2, file_2) = (
        create_schema_files(tmp_path, (SCHEMA_1, SCHEMA_2))
    )

    el = EventLog()

    el.register_schema_file(file_1)
    with pytest.raises(ValueError):
        el.register_schema_file(file_2, duplicate='string')
