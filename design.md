# EventLogging design

This document supplements `implementations.md` and has sections detailing the
the eventlogging design that can be common to various parts of the Jupyter
ecosystem. These two documents will co-evolve - as we think more about
implementation, the design will change, and vice versa.

## Why collect data?

The primary reasons for collecting such data are:

1. Better understanding of *usage* of their infrastructure. This 
   might be for capacity planning, metrics, billing, etc

2. *Auditing* requirements - for security or legal reasons. Our
   Telemetry work in the Jupyter project is necessary but not
   sufficient for this, since it might have more stringent
   requirements around secure provenance & anti-tampering.

4. UX / UI Events from end user behavior. This is often
   targeted measurements to help UX designers / developers
   determine if particular UX decisions are meeting their
   goals.

3. *Operational* metrics. Prometheus metrics should be used for
   most operational metrics (error rates, percentiles of server
   or kernel start times, memory usage, etc). However, some
   operational data is much more useful when lossless than 
   when sampled, such as server start times or contentmanager
   usage.

## Metrics vs Events

Both Metrics and Events are telemetry, but are fundamentally
different. Katy Farmer [explains it](https://thenewstack.io/what-is-the-difference-between-metrics-and-events/) 
thus:

> I want to keep track of my piggy bank closely. Right now, there’s only one
> metric I care about: total funds. Anyone can put money into my piggy bank, so
> I want to report the total funds at a one-minute interval. This means that
> every minute, my database will receive a data point with the timestamp and
> the amount of total funds in my piggy bank.
>
> Now, I want to track specific events for my piggy bank: deposits and
> withdrawals. When a deposit occurs, my database will receive a data point
> with the “deposit” tag, the timestamp and the amount of the deposit.
> Similarly, when a withdrawal occurs, my database will receive a data point
> with the “withdrawal” tag, the timestamp and the amount of the withdrawal.
>
> Imagine now that this is the same basic idea behind online banking. We could
> add more metadata to add detail to the events, like attaching a user ID to a
> deposit or withdrawal.

Metrics let us answer questions like 'what is the 99th percentile start time
for our user servers over the last 24 hours?' or 'what is the current rate
of 5xx errors in notebook servers running on machines with GPUs?'. They have
limited cardinality, and are usually aggregated at the source. Usually,
they are regularly pulled into a central location at regular intervals. They
rarely contain any PII, although they might leak some if we are not careful. These
are primarily operational. We already support metrics via the [prometheus]
(https://prometheus.io/) protocol in [JupyterHub](https://github.com/jupyterhub/jupyterhub/pull/1581),
[Notebook Server](https://github.com/jupyter/notebook/pull/3490) and
[BinderHub](https://github.com/jupyterhub/binderhub/pull/150). This is
heavily used in a bunch of places - see the public [grafana instance]
(https://grafana.mybinder.org/) showing visualizations from metrics
data, and documentation about [what is collected](https://mybinder-sre.readthedocs.io/en/latest/components/metrics.html)

Events let us answer questions like 'which users opened a notebook named
this in the last 48h?' or 'what JupyterLab commands have been executed
most when running with an IPython kernel'. They have much more information
in them, and do not happen with any regularity. Usually, they are also
'pushed' to a centralized location, and often contain PII - so need
to be treated carefully. BinderHub [emits events](https://binderhub.readthedocs.io/en/latest/eventlogging.html)
around repos launched there, the mybinder.org team has a [very small
pipeline](https://github.com/jupyterhub/mybinder.org-deploy/tree/master/images/analytics-publisher)
that cleans these events and publishes them at [archive.analytics.mybinder.org](https://github.com/jupyterhub/mybinder.org-deploy/tree/master/images/analytics-publisher)
for the world to see.

This document focuses primarily on *Events*, and doesn't talk much about metrics.

## Stakeholders

1. End Users

   Primary stakeholder, since it is their data. They have a right
   to know what information is being collected about them. We should
   make this the default, and provide automated, easy to understand
   ways for them to see what is collected about them.

2. Operators

   The operators of the infrastructure where various Jupyter components
   run are the folks interested in collecting various bits of Events.
   They have to:

   a. Explicitly decide what kinds of Events at what level they are going to
      be collecting and storing

   b. Configure where these Events needs to go. It should be very
      easy for them to integrate this with the rest of their infrastructure.

   By default, we should not store any Events unless an operator
   explicitly opts into it.

3. Developers

   Developers will be emitting Events from various parts of the code.
   They should only be concerned about emitting Events, and
   not about policy enforcement around what should be kept and
   where it should be stored. We should also provide easy
   interfaces for them to emit information in various places
   (backends, frontends, extensions, kernels, etc)

4. Analysts

   These are the folks actually using the event data to make
   decisions, and hence the ultimate consumers of all this data.
   They should be able to clearly tell what the various fields
   in the data represent, and how complete it is. We should also
   make it easy for the data to be easily consumable by common
   analyst tools - such as pandas, databases, data lakes, etc

## Other systems to study

We aren't the first group to try design a unified eventlogging
system that is easy to use, transparent and privacy preserving
by default. Here are some examples of prior art we can draw
inspiration from.

* Wikimedia's [EventLogging](https://www.mediawiki.org/wiki/Extension:EventLogging/Guide)

  A simple and versatile system that can scale from the needs
  of a small organization running MediaWiki to the 7th largest
  Website in the world. The [Guide](https://www.mediawiki.org/wiki/Extension:EventLogging/Guide)
  lays out the principles behind how things work and why they
  do the way they do. The [Operational Information Page](https://wikitech.wikimedia.org/wiki/Analytics/Systems/EventLogging)
  shows how this is configured in a large scale installation.

  Let's take an example case to illustrate this.

  Each eventlogging use case must be documented in a public
  schema. [This schema](https://meta.wikimedia.org/wiki/Schema:ServerSideAccountCreation)
  documents events collected about account creation events.
  This is very useful for a variety of stakeholders.

    1. Users can see what information is being collected about
       them if they wish.

    2. Analysts know exactly what each field in their dataset means

    3. Operators can use this to perform automatic data purging,
       anonymizing or other retention policies easily. See
       how [wikimedia does it](https://wikitech.wikimedia.org/wiki/Analytics/Systems/EventLogging/Data_retention_and_auto-purging),
       to be compliant with GDPR and friends.

    4. Developers can easily log events that conform to the schema
       with standardized libraries that are provided for them,
       without having to worry about policy around recording and
       retention. See some [sample code](https://www.mediawiki.org/wiki/Extension:EventLogging/Guide#Underlying_technology)
       to get a feel for how it is.

* Mozilla's Telemetry system

  Firefox runs on a lot of browsers, and has a lot of very privacy conscious
  users & developers. Mozilla has a well thought out [data collection policy]
  (https://wiki.mozilla.org/Firefox/Data_Collection). 
  
  There is a [technical overview](https://firefox-source-docs.mozilla.org/toolkit/components/telemetry/telemetry/start/adding-a-new-probe.html)
  of various capabilities available. Their [events](https://firefox-source-docs.mozilla.org/toolkit/components/telemetry/telemetry/collection/events.html)
  system is most similar to what we want here. Similar to the wikimedia example,
  every event must have a corresponding schema, and you can see all the
  schemas in their [repository](https://dxr.mozilla.org/mozilla-central/source/toolkit/components/telemetry/Events.yaml).
  They also provide easy ways for developers to [emit events](https://firefox-source-docs.mozilla.org/toolkit/components/telemetry/telemetry/collection/events.html#the-api)
  from the frontend JS.

  There is a lot more information in their [telemetry data portal](https://docs.telemetry.mozilla.org/),
  particularly around how analysts can work with this data.

* Debian 'popularity contest'

  The debian project has an opt-in way to try map the popularity of
  various packages used in end user systems with the [popularity
  contest](https://popcon.debian.org/). It is a purely opt-in system,
  and records packages installed in the system and the frequency
  of their use. This is [sortof anonymously, sortof securely](https://popcon.debian.org/FAQ) 
  sent to a centralized server, which then produces useful graphs.
  [Ubuntu](https://popcon.ubuntu.com/) and [NeuroDebian](http://neuro.debian.net/popcon/)
  run versions of this as well for their own packages.

  This is different from the other systems in being extremely
  single purpose, and not particularly secure in terms of user
  privacy. This model might be useful for particular things that
  need to work across a large swath of the ecosystem - such as
  package usage metrics - but is of limited use in Jupyter itself.

* Homebrew's analytics

  The popular OS X package manager [homebrew](https://brew.sh]
  [collects information](https://github.com/Homebrew/brew/blob/master/docs/Analytics.md) about 
  usage with Google Analytics. This is very similar to the Debian Popularity
  contest system, except it sends events to a third party (Google Analytics)
  instead. You can opt out of it if you wish.

* Bloomberg?

  Paul Ivanov mentioned that Bloomberg has their own data collection
  system around JupyterLab. Would be great to hear more details of that
  here.

* Other organizations

  Everyone operating at scale has some way of doing this kind of analytics
  pipeline. Would be great to add more info here!

## Design proposal

1. *Schema*

   Each event type needs a [JSON Schema](https://json-schema.org/) associated
   with this. This schema is versioned to allow analysts, operators
   and users to see when new fields are added / removed. The descriptions
   should also be clear enough to inform users of what is being collected,
   and analysts of what they are actually analyzing. We could also use this
   to mark specific fields as PII, which can then be automatically mangled,
   anonymized or dropped.

2. *EventLogging Python API*

   A simple python API that lets users in serverside code (JupyterHub,
   Notebook Server, Kernel, etc) emit events. This will:

   1. Validate the events to make sure they conform to the schema
      they claim to represent.
   2. Look at traitlet configuration to see if the events should be
      dropped, and immediately drop it if so. So nothing leaves the
      process unless explicitly configured to do so.
   3. Filter / obfuscate / drop PII if configured so.
   3. Wrap the event in an *event capsule* with common information
      for all events - timestamp (of sufficient granularity),
      schema reference, origin, etc.
   4. Emit the event to a given 'sink'. We should leverage the 
      ecosystem built around Python Loggers for this, so we can
      send events to a wide variety of sources - [files](https://docs.python.org/3/library/logging.handlers.html#filehandler),
      [files with automatic rotation](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler),
      [arbitrary HTTP output](https://docs.python.org/3/library/logging.handlers.html#httphandler),
      [kafka](https://pypi.org/project/python-kafka-logger/),
      [Google Cloud's Stackdrive](https://pypi.org/project/google-cloud-logging/),
      [AWS CloudWatch](https://github.com/kislyuk/watchtower),
      [ElasticSearch](https://github.com/kislyuk/watchtower)
      and many many more. This should help integrate with whatever
      systems the organization is already using.

   This helps us centralize all the processing around event validity,
   PII handling and sink configuration. Organizations can then decide
   what to do with the events afterwards.

3. *EventLogging REST API*

   This is a HTTP Endpoint to the Python API, and is a way for frontend
   JavaScript and other remote clients to emit events. This is an HTTP
   interface, and could exist in many places:

   1. Inside JupyterHub, and all events can be sent via that.
   2. Inside Jupyter Notebook Server, so it can collect info from
      the user running it. The Notebook Server can then send it
      someplace.
   3. A standalone service, that can be sent events from everywhere.

  By separating (2) and (3), we can cater to a variety of scales
  and use cases.

4. *EventLogging JavaScript API*

   This is the equivalent to (1), but in JavaScript.

   It should receive configuration in a similar way as (1) and (2), but be
   able to send them to various sinks *directly* instead of being forced to
   go through (3). This is very useful in cases where events should be sent
   directly to a pre-existing collection service - such as Google Analytics
   or mixpanel. Those can be supported as various sinks that plug into this
   API, so the code that is emitting the events can remain agnostic to where
   they are being sent.

   The default sink can be (3), but we should make sure we implement
   at least 1 more sink to begin with so we don't overfit our API design.

   We should be careful to make sure that these events still conform to
   schemas, need to be explicitly turned on in configuration, and follow
   all the other expectations we have around eventlogging data.

5. *User consent / information UI*

   Every application collecting data should have a way to make it
   clear to the user what is being collected, and possibly ways
   to turn it off. We could possibly let admins configure opt-in /
   opt-out options.

## Open questions

Here's a list of open questions.

1. How to reference schemas in ways people can find them? Current
   example points to URLs that don't exist, purely as a way to
   namespace them. Perhaps we should have them point to URLs that
   *do* exist?

2. How do we signal strongly that telemetry / events are never sent
   to the Jupyter project / 3rd party unless you explicitly configure
   it to do so? This is a common meaning of the word 'telemetry'
   today, so we need to make sure we communicate clearly what this
   is, what this isn't, and what it can be used for. Same applies
   to communicating that nothing is collected or emitted anywhere,
   despite the possible presence of emission code in the codebase.

3. Add yours here!