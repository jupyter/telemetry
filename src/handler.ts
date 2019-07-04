// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import {
  URLExt
} from '@jupyterlab/coreutils';

import {
  ServerConnection
} from '@jupyterlab/services';

import {
  ReadonlyJSONObject
} from '@phosphor/coreutils';

/**
 * The handler for telemetry data.
 */
export
class TelemetryHandler {
  /**
   * Create a new telemetry handler.
   */
  constructor(options: TelemetryHandler.IOptions = { }) {
    this.serverSettings = options.serverSettings ||
      ServerConnection.makeSettings();
  }

  /**
   * The server settings used to make API requests.
   */
  readonly serverSettings: ServerConnection.ISettings;

  /**
   * Emit an event to the server
   *
   * This may implement batching and other performance optimizations
   * in the future.
   *
   * @param event - The event being emitted
   *
   * @returns A promise that resolves when saving is complete or rejects with
   * a `ServerConnection.IError`.
   */
  emit(event: Telemetry.ICommandInvocation): Promise<void> {
    const { serverSettings } = this;
    const url = URLExt.join(serverSettings.baseUrl, 'eventlog');
    const full_event = {
      'schema': 'lab.jupyter.org/command-invocations',
      'version': 1,
      'event': event
    }
    const init = {
      body: JSON.stringify(full_event),
      method: 'PUT'
    };
    const promise = ServerConnection.makeRequest(url, init, serverSettings);

    return promise.then(response => {
      if (response.status !== 204) {
        throw new ServerConnection.ResponseError(response);
      }
      return undefined;
    });
  }
}


/**
 * A namespace for `TelemetryHandler` statics.
 */
export
namespace TelemetryHandler {
  /**
   * The instantiation options for a telemetry handler.
   */
  export
  interface IOptions {
    /**
     * The server settings used to make API requests.
     */
    serverSettings?: ServerConnection.ISettings;
  }
}


/**
 * A namespace for telemetry API interfaces.
 */
export
namespace Telemetry {
  /**
   * An interface describing an executed command.
   *
   * FIXME: Automatically generate these from the schema?
   */
  export
  interface ICommandInvocation {
    /**
     * UUID representing current session
     */
    readonly session_id: string;

    /**
     * The id of the command.
     */
    readonly command_id: string;

    /**
     * The args of the command.
     */
    readonly command_args: ReadonlyJSONObject;
  }
}
