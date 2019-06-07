# Jupyter telemetry enhancement proposal

| Item       | Value                                                                                                                        |
|------------|------------------------------------------------------------------------------------------------------------------------------|
| JEP Number | XX                                                                                                                           |
| Title      | Jupyter telemetry                                                                                                   |
| Authors    |  |
| Status     | Draft                                                                                                                        |
| Type       | S - [Standards Track](https://www.python.org/dev/peps/#pep-types-key) JEP                                                    |
| Created    | 5 June 2019                                                                                                           |
| History    | 5 June 2019

## Problem

Telemetry data serves a number of purposes for organizations deploying Jupyter: i) operational monitoring, ii) security monitoring / intrusion detection, iii) compliance auditing, and iv) a-posteriori analysis of the platform’s usage and design–i.e. as a UX research tool. This must be done in a transparent and understandable manner for end-users. Jupyter components and extension developers interested in publishing events must be incentivized to follow the system's interface and patterns rather then rolling out their own.

### Personas

* **Jupyter Users** are the primary stakeholder since it is their data.
* **Jupyter extension developers** will be emitting events from both the server-side and the browser-side code.
* **Jupyter operators** handle the infrastructure deployments and are interested in collecting various bits of events.
* **Analysts** consume the final stored data and visualize and interpret it.

### User Stories

1. As a Jupyter user, I can view and understand the events being collected, so that I have visibility into what information is being collected.
2. As a Jupyter user, I need to opt-in to event collection, so that I can choose what data about my usage is gathered.
3. As a Jupyter extension developer, I can publish custom events using a well defined interface, from the browser as well as the server.
4. As a Jupyter operator, I can configure events sinks for my deployment, so that I have control over where events are sent to.
5. As a Jupyter operator, I can write a custom event sink for my deployment, so that I can control where event data is stored.
6. As a Jupyter operator, I can decide what kinds and levels of events are going to be collected and stored.
7. As a Jupyter operator, I can configure opt-in or opt-out for the users in my deployment.
8. As an analyst,  I can clearly tell what the fields in the data represent so that I can interpret and make decisions from that data.

## Proposed Enhancement

The enhancement spans two categories - general concepts applicable across all Jupyter components, and the implementation for each concept for each Jupyter component.

**General concepts:**

* Event schema: The schema for a given event which is respected by all the Jupyter components across the event's lifecycle.
* Event sinks: The "backends" which handle publishing the event to its final storage location.

**Jupyter components:**

* Jupyter server
* JupyterLab
* JupyterHub
* Jupyter Classic

## Detailed Explanation

### Event Schema

Each event is published conforming a given event schema and this is the contract followed by each step in the event lifecycle. These are referred to by all publishers regardless of whether the event comes from the server or the browser.

Example event schema

```json
{
    "name": "org.jupyter.kernel_lifecycle_event",
    "version": 1,
    "title": "Event emitted when a kernel lifecycle state changes",
    "description": "Records each invocation of any command in JupyterLab",
    "type": "object",
    "args": {
        "kernel_name": {
            "type": "string",
            "description": "Name of the kernel"
        },
        "state": {
            "type": "string",
            "description": "The new state of the kernel"
        }
    }
}
```

Schema validation is done in the core telemetry framework that routes events from publishers to sinks, so that each event sink does not need to implement schema validation.

**Open Questions**:

* How do organizations deploy custom schemas?
* Where are the schemas for public events stored?

### Event Sinks

Event sinks are the backends where events published to.  Event sinks can be configured from the browser as well as the server. Custom sinks can be implemented by extending the interface for the given Jupyter component. 
See [Python interface](#python-event-sink-interface) and the [JupyterLab interface](#jupyterlab-event-sink-interface)

### Jupyter Server

#### Python publisher library

The Python event publisher library provides extension developers and other internal components an interface to record events. This is agnostic of the event sink back-end and the other deployment configurations.

```python
import jupyter.telemetry as telemetry

telemetry.record_event(
    name='org.jupyter.kernel_lifecycle_event',
    schema_version='1',
    args={
        'kernel_name': 'python3',
        'state': 'restarted'
    }
)
```

#### Python Event Sink Interface

The event sink interface

```python
class MyCustomEventSink(JupyterEventSink):

    def consume_event(event_data):
        # Business logic to publish event into the backend.
```

#### Configuration

A setting on the Jupyter server allows operators to configure various options of the event sinks such as:

* The event sink implementations
* The list of event names to whitelist or blacklist

```bash
jupyter notebook \
    --NotebookApp.telemetry_event_sinks=mypackage.sinks.MyCustomEventSink,mypackage.sinks.AnotherCustomEventSink \
    --NotebookApp.blacklisted_events='org.jupyter.someevent' \
```

#### Core event router

The implementation of the `telemetry.record_event` method which handles

* Schema validation
* Adds event metadata such as `creationTime`
* Routing events to configured sinks
* Filters events based on the configuration
* (Optionally) Aggregation and data cleaning.

This part should be scalable to handle the volume of events and implement some sort of pub-sub design pattern.

```python
def record_event(name, schema_version, args):
    # validate schema
    # add metadata
    # get configured sinks
    # send event to sinks
```

#### REST Endpoint

In addition to the above sub-components, a REST interface is exposed on the Jupyter server to allow remote clients and the frontend to publish events into the server. The interface for this is similar to the [Python publisher library](#python-publisher-library)

```json
HTTP PUT /api/telemetry/event
{
    "name" : "org.jupyter.kernel_lifecycle_event",
    "schema_version : "1",
    "args" : {
        "kernel_name": "python3",
        "state": "restarted"
    }
}
```

#### Open Questions

1. Is this work done on the standalone jupyter-server implementation or on the classic jupyter/notebook?

### JupyterLab

There are quite a few analytics frameworks that send events directly from the browser, so the round trip to the server can be avoided in certain deployments. Additionally, JupyterLab also publishes "platform" events which are subscribed to and published to the event sinks.

All the sub-components defined in the [Jupyter server](#jupyter-server) section are applicable here as well.

#### JupyterLab publisher library

An interface to expose to JupyterLab extension developers to be able to publish custom events. This is similar to [this](https://github.com/jupyterlab/jupyterlab-telemetry/)

```typescript
import {recordEvent} from '@jupyterlab/telemetry'

recordEvent({
    name: 'org.jupyter.jupyterlab_command',
    schema_version: '1',
    args: {
        'commandName': 'newFile'
    }
})
```

#### JupyterLab Event Sink Interface

An interface to expose to operators writing their own custom sink (as JupyterLab extensions themselves) and register themselves with the core routing components. The default event sink implementation is to publish to the [Server REST Endpoint](#rest-endpoint).

```typescript
import {EventSink, EventData} from '@jupyterlab/telemetry'

export class MyCustomEventSink implements EventSink {
    handle_event(eventData: EventData): Promise<void> {
        // Business logic to publish event to backend.
    }
}
```

#### JupyterLab Configuration

The ability to configure the event sinks to publish to as well as events to blacklist or whitelist events. This can likely be accomplished via JupyterLab settings and the JupyterLab dependency management mechanism.

The JupyterLab telemetry extension provides `Token<EventSink>` that event sink implementations can depend on and register themselves with the  core event router.

#### JupyterLab Core event router

The implementation of the `@jupyterlab/telemetry/recordEvent` method which handles routing events to the configured sinks and additionally:

* Schema validation
* Adds event metadata such as `creationTime`
* Filters events based on the configuration
* (Optionally) Aggregation and data cleaning.

#### User opt-in

Since JupyterLab is the user facing component, it also contains UX features to give more visibility and transparency to the Jupyter user. In general, every component should make it clear to the user what data is being collected and possible ways to turn it off.

* UI for opting in or opting out of telemetry data collection
* UI for showing the list of events that are currently being collected.

### JupyterHub

(This section needs to be filled out)

### Jupyter Classic

The proposal for Jupyter Classis is to have a convenience JS library that can be used to pubish events to the server [REST Endpoint](#rest-endpoint).
This ensures that we provide support for Jupyter Classic but can rely on the Jupyter Server to do much of the heavy-lifting by relying on the Core Event Router, Event Sinks, and configuration done at the server level.

```javascript

var telemetry = require('jupyter-telemetry-js')

telemetry.record_event(
    name='org.jupyter.kernel_lifecycle_event',
    schema_version='1',
    args={
        'kernel_name': 'python3',
        'state': 'restarted'
    }
)
```

### Data protection

(This section needs to be filled out)

* What guidance do we provide? How do we provide this?
* What building blocks do we provide?

## Pros and Cons

PROS

* Implementation shares common principles and components across the Jupyter components.
* Decoupling between event publishers and event consumers.
* Flexible configuration for Jupyter operators to configure event sinks and event names.

CONS

* How do we enable data protection by default? (Just marking a event attribute as PII may not solve this)
* What guidance and building blocks do we provide for compliance programs such as GDPR

## Appendix

### Tenets

(These are taken from [Brian's initial issue](https://github.com/jupyterlab/team-compass/issues/4).)

There are certainly ethical and legal questions around telemetry systems. To address these, the following tenets of the telemetry system are proposed:

* **Data protection by design and default.** Jupyter and its telemetry system should come with builtin tools that enable safe and secure deployments with all types of data. See [Art. 25 of GDPR](https://gdpr-info.eu/art-25-gdpr/) for details about this tenet.
* **Make it easy to do the right things by default.** There are many ways to collect and use telemetry data that are illegal and/or irresponsible. Jupyter’s telemetry system should encode best practices and make it easy for operators to be responsible and comply with relevant laws.
* **Choice in balancing tradeoffs.** There are two types of data JupyterLab: 1) the actual datasets users are working with in notebooks, and 2) telemetry data about the Jupyter users. At times, protecting these two types of data at the same time will require tradeoffs. For example, if a deployment is doing research with sensitive HIPAA or FERPA data, the operators need to closely monitor every action taken by its researchers using JupyterLab to ensure the sensitive data is used appropriately. At the same time, in some jurisdictions (EU) Jupyter users may be protected by local laws (GDPR) about what telemetry data can be recorded, how it can be used, the terms of that usage.
* **Don't ignore the need for telemetry**. Organizations deploying Jupyter need to collect telemetry for a range of purposes. If we ignore this need, they will route around the project, with potential legal and ethical complications. By being proactive, we can establish best practices and guardrails.

### References

1. Original write up by ellisonbg@ [https://github.com/jupyterlab/team-compass/issues/4](https://github.com/jupyterlab/team-compass/issues/4)
2. Wikimedia [telemetry system](https://m.mediawiki.org/wiki/Extension:EventLogging/Guide)
3. Initial strawman [design doc](https://github.com/jupyterlab/jupyterlab-telemetry/blob/master/design.md)
4. [Mozilla Telemetry System](https://wiki.mozilla.org/Telemetry)
