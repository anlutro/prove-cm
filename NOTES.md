# Prove

A configuration managing tool.

## Concepts

- Master: A host that controls other hosts, source of authority for configuration etc.. This can be a centralized server with a long-running master daemon which provides a HTTP API or similar, or just your workstation running commands ad-hoc.
- Targets: Hosts that the master can configure. These targets can be reached by various transports.
- Executors: Ways for master to talk to hosts
  - Local execution (agentless)
  - SSH (agentless)
  - Remote execution using an agent and a transport
- Transports define a way for masters and targets to talk to eachother: ZeroMQ, HTTP, UDP, TCP...
- Agent: Daemon that runs on remote hosts for the master to connect to and give instructions
- Catalog: Various data stored by the master to know what to do on different targets
  - Variables is a dictionary of data assigned on a per-host basis
  - States are definitions of how a system should be configured
  - Roles are a way to easily apply both variables and states to hosts, reducing duplication
  - Components are a way to modularise variables and states, making them re-usable
- Operations are things that should be done by Prove. Consist of 2 parts:
  - Commands: Initiated by the master to tell the target what to do.
  - Actions: Invoked on the target somehow and does what needs to be done.

### States

Write state files in YAML, templated YAML, JSON, or Python. Mako + YAML should
be the default.

States must be able to flexibly and dynamicly define dependencies. It must be
possible to run states more than once without having to duplicate states or
write custom states. For example:

1. Generate nginx configuration for new domain
2. Reload nginx
3. Generate TLS certificates for the domain
4. Generate nginx configuration, with new variables (TLS certificate paths)
5. Reload nginx, again

Some states should be "lazy" - that is, they only run if specifically requested
to do so. Examples of this would be the restarting of a service. This is similar
to handlers in Ansible, or states with "onchanges" in Salt.

States request other states to run by notifying them. This can also be inverted
- a state can specify which other states it should be notified on by specifying
that it's listening to them. Similar to "onchanges_in" in Salt.

There should be a set of "meta" state functions that can be used for stuff like
gathering multiple states into one so that it's easy for other states to require
all of them at once. These meta functions will likely not be able to fit into
the traditional state function pattern. Maybe draw inspiration from the block
system in Ansible.

Some states will be too difficult to code in a way that lets it work over SSH.
These should give the user a warning that they need to use an agent.

## State types

StateFile
	contains multiple State
		contains multiple StatePart

StateRun
	contains multiple StateInvocation
		contains multiple StatePartInvocation
	contains multiple RootNode
		contains multiple Node
			contains multiple dependency Node
			contains multiple notify/notify_failure Node
