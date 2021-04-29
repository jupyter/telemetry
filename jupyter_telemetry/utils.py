
class JupyterTelemetryException(Exception):
    """Exceptions for Jupyter Telemetry"""


def event_schema(name, version, schema=None):
    """Decorator for wrapping methods with information about
    the type of event data emitted by the method.
    """
    def method_wrapper(method):
        # Needs to wrap a method, so adding one more layer
        # of depth to handle self.
        def jupyter_telemetry_event_wrapper(self, *args, **kwargs):
            self.eventlog._set_incoming_event(name, version)
            output = method(self, *args, **kwargs)
            # Flush the current event.
            self._clear_incoming_event()
            return output
        return jupyter_telemetry_event_wrapper

    return method_wrapper
