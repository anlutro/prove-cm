# Prove

A configuration managing tool.

## Concepts

- Master: A host that controls other hosts, source of authority for configuration etc.
- Targets: Hosts that the master can configure. These targets can be reached by various transports
- Agent: Daemon that runs on remote hosts for the master to connect to and give instructions
- Transports: Ways for master to configure hosts
  - SSH and local execution are agentless
  - ZeroMQ, HTTP, UDP, TCP require an agent to be running

- Variables is a dictionary of data assigned on a per-host basis
- States are definitions of how a system should be configured
- Roles are a way to easily apply both variables and states to hosts, reducing duplication
- Components are a way to modularise variables and states, making them re-usable

## Design goals

A master should be able to connect to many different targets using different
transports. Using a different console command for SSH vs remote agents should
not be necessary.

### States

Write state files in YAML, templated YAML, JSON, or Python. Mako + YAML should
be the default.

States must be able to flexibly and dynamicly define dependencies. It must be
possible to run states more than once without having to duplicate states or
write custom states. For example:

1. Configuration changes due to host variable changing (state A)
2. Service reload (state B)
3. Run a script to generate some new files
4. Configuration changes to use the new files (state A)
5. Service reload (state B)

Some states should be "lazy" - that is, they only run if specifically requested
to do so. Examples of this would be the restarting of a service.

States request other states to run by notifying them. This can also be inverted
- a state can specify which other states it should be notified on by specifying
that it's listening to them.

There should be a set of "meta" state functions that can be used for stuff like
gathering multiple states into one so that it's easy for other states to require
all of them at once. These meta functions will likely not be able to fit into
the traditional state function pattern.

Some states will be too difficult to code in a way that lets it work over SSH.
These should give the user a warning that they need to use an agent.
