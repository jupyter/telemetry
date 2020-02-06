import os
import json
import pathlib
import textwrap
from ruamel.yaml import YAML
# Cannot import sphinx-jsonschema using import statement
# because the name contains a hyphen.
JsonSchema = __import__('sphinx-jsonschema').JsonSchema


yaml = YAML(typ='safe')


# Use the JsonSchema directive from sphinx-jsonschema,
# But replace the directive name so that we don't
# require this users to list both the 'jupyter_telemetry_schema'
# and 'sphinx-jsonschema' extensions in their conf.py.
class JupyterTelemetrySchema(JsonSchema):

    def __init__(self, directive, *args, **kwargs):
        # There is an `assert` statement in JsonSchema that
        # requires the directive to == 'jsonschema'.
        # Here we substitute this directive in, even though
        # the directive is actually 'jupyter_telemetry_schema'.
        super(JupyterTelemetrySchema, self).__init__(
            'jsonschema',
            *args, **kwargs
        )


def create_event_schema_docs(app, config):

    src = config.jupyter_telemetry_schema_source
    out = config.jupyter_telemetry_schema_output
    title = config.jupyter_telemetry_index_title

    # If src or out path is not given, don't do anything.
    if src is None:
        return

    if out is None:
        return

    src_base_path = pathlib.Path(src)
    out_base_path = pathlib.Path(out)

    # Write schema RST files.
    schema_paths = []
    for (base, _, files) in os.walk(src):
        for f in files:
            src_path = pathlib.Path(base).joinpath(f)
            # Verify that the file is a JSON or YAML file, otherwise ignore.
            if src_path.suffix in ['.json', 'yaml']:
                rel_path = src_path.relative_to(src_base_path)
                out_path = out_base_path.joinpath(rel_path)
                out_path = out_path.with_suffix('.rst')

                data = yaml.load(src_path.read_text())
                json_data = json.dumps(data, indent=4)
                doc_text = ".. jupyter_telemetry_schema::\n\n" + textwrap.indent(json_data, '\t')

                # Make the directory if it doesn't exist.
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(doc_text)

                index_path = rel_path.with_suffix('')
                schema_paths.append(str(index_path))

    # Write the index.
    index = out_base_path.joinpath('index.rst')
    schema_list = textwrap.indent('\n'.join(schema_paths), '\t')
    index_text = (
        "{}".format(title),
        "{}\n".format("="*len(title)),
        ".. toctree::\n",
        "{}".format(schema_list)
    )
    index.write_text('\n'.join(index_text))


def setup(app):
    app.add_config_value("jupyter_telemetry_schema_source", None, "html")
    app.add_config_value("jupyter_telemetry_schema_output", None, "html")
    app.add_config_value("jupyter_telemetry_index_title", "Event Schemas", "html")
    app.add_directive('jupyter_telemetry_schema', JupyterTelemetrySchema)

    # Build event schema source files before reading+building docs.
    app.connect("config-inited", create_event_schema_docs)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
