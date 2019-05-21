import logging

c.EventLog.allowed_schemas = [
    'lab.jupyter.org/command-invocations'
]

def make_eventlog_sinks(eventlog):
    # As an example, let's write these to local file
    return [logging.FileHandler('events.log')]

c.EventLog.handlers_maker = make_eventlog_sinks