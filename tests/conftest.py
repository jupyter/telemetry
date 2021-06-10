from jupyter_telemetry.eventschema import JSON_SCHEMA_VALIDATORS


def pytest_generate_tests(metafunc):
    if "json_validator" in metafunc.fixturenames:
        metafunc.parametrize("json_validator", JSON_SCHEMA_VALIDATORS.keys())
