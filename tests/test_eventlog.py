import pytest
import logging
from traitlets.config.loader import PyFileConfigLoader
from traitlets import TraitError

from jupyter_telemetry.eventlog import EventLog

GOOD_CONFIG = """
import logging

c.EventLog.handlers = [
    logging.StreamHandler()
]
"""

BAD_CONFIG = """
import logging

c.EventLog.handlers = [
    0
]
"""


def get_config_from_file(path, content):
    # Write config file
    filename = 'config.py'
    config_file = path / filename
    config_file.write_text(content)

    # Load written file.
    loader = PyFileConfigLoader(filename, path=str(path))
    cfg = loader.load_config()
    return cfg


def test_good_config_file(tmp_path):
    cfg = get_config_from_file(tmp_path, GOOD_CONFIG)

    # Pass config to EventLog
    e = EventLog(config=cfg)

    # Assert the 
    assert len(e.handlers) > 0
    assert isinstance(e.handlers[0], logging.Handler)


def test_bad_config_file(tmp_path):
    cfg = get_config_from_file(tmp_path, BAD_CONFIG)

    with pytest.raises(TraitError):
        e = EventLog(config=cfg)
