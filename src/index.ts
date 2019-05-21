// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import {
  JupyterLab, JupyterLabPlugin
} from '@jupyterlab/application';
import {
  UUID
} from '@phosphor/coreutils';

import {
  Widget
} from '@phosphor/widgets';

import {
  TelemetryHandler
} from './handler';

import '../style/index.css';


/**
 * Initialization data for the jupyterlab-telemetry extension.
 */
const extension: JupyterLabPlugin<void> = {
  id: 'jupyterlab-telemetry',
  autoStart: true,
  activate: (app: JupyterLab) => {
    const { commands } = app;
    const handler = new TelemetryHandler();

    // Make a uuid for this session, which will be its
    // key in the session data.
    const session_id = UUID.uuid4();
    console.log("WOOHOOO?")

    app.restored.then(() => {
      // Add a telemetry icon to the top bar.
      // We do it after the app has been restored to place it
      // at the right.
      const widget = new Widget();
      widget.addClass('jp-telemetry-icon');
      widget.id = 'telemetry:icon';
      widget.node.title = 'Telemetry data is being collected';
      app.shell.addToTopArea(widget);


      // When a command is executed, emit it
      commands.commandExecuted.connect((registry, command) => {
        console.log("A COMMAND HAS BEEN EXECUTED YO");
        handler.emit({
          session_id: session_id,
          command_id: command.id,
          command_args: command.args
        })
      });
    });
  }
};

export default extension;
