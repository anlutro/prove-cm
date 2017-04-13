Entry points are the `prove.cli` submodules, most importantly `prove.cli.action_runner` which is the default `prove` executable.

When you invoke a command like `prove states`, these things happen:

- An instance of `prove.application.Application` is created, which reads configuration files to find target hosts as well as available states, files, components and more.
- For each target, a `prove.environment.Environment` is created, which holds information about the target's options, variables, state files and more.
- An instance of `prove.locator.Locator` will find and load files of various types and make them available to the Python runtime.
- The correct submodule of `prove.actions` is found. In the example of `prove states`, this is `prove.actions.states`.
- An instance of `prove.states.StatesCommand` is created and invoked on the machine you're running `prove` from.

From here on it gets a bit trickier. There is a corresponding `Action` class for each `Command` class if anything needs to be invoked on the target host. How exactly this happens depends on the executor used - if using the `local` executor, everything happens in the same python process on the same machine. If using the `ssh` executor, an SSH connection is established and the python process runs commands across this connection. If the `remote` executor is used, a separate daemon is running on the target host, and while the `Command` class is invoked on the master, the `Action` class is invoked on the target host.

Regardless of transport, the `Action` class and everything it invokes has to work across all types of executors. This means, for example, not using `subprocess.Popen`, but instead using `session.run_command`, which contains the appropriate abstractions.

## Session abstractions

The abstract session class is defined in `prove.executor`. Because it has to work across multiple types of executors it has very limited functionality:

- Executing shell commands on the remote system
- Uploading and downloading files to/from the remote system

More advanced python logic can of course be used, but be aware that this logic is sometimes executed on the master (the machine running the `prove` command), but other times on the target host.

## State functions

The `states` command is the most complex and useful one. It creates an instance of `prove.states.runner.StateRunner` which does the heavy lifting in terms of figuring out the correct order of states, making sure that states don't run if a pre-requisite failed, and so on.

Each state consists of a unique ID, and one or more state function calls, such as `package.installed`. These are loaded from `prove.state_functions`. This is the main place to add functionality.
