# Prove

Prove is a configuration management system, similar to Puppet, Chef, Ansible and Salt.

## Installation

	$ pip install --user prove

This will install prove into `$HOME/.local`. I recommend adding
`$HOME/.local/bin` to your `$PATH`.

Alternatively, if you're not concerned about using sudo:

	$ sudo pip install prove

You may need to install libffi-dev through your system's package manager.

## Development

For development and testing, use a virtualenv:

	$ cd /path/to/prove
	$ virtualenv -p python3 .
	$ source bin/activate
	$ pip install -e .
	$ pip install -r requirements_dev.txt

Tests are ran with pytest:

	$ py.test

To generate test coverage reports:

	$ py.test --cov=prove

Linting is done with pylint:

	$ pylint prove

## Try out the remote system

Open two terminals, activate the virtualenv in both. In the first, run the agent:

	$ prove-agent -c conf/test/prove.yml

Next, run prove against the host:

	$ prove -c conf/test/prove.yml -t remote.localhost cmd 'echo hello world'
	$ prove -c conf/test/prove.yml -t remote.localhost states

You can also test it by running the agent in a Vagrant VM:

	$ sudo apt-get install python3
	$ PYTHONPATH=/vagrant /vagrant/bin/python -m prove.cli.agent -c /vagrant/conf/vagrant/prove.yml -b 0.0.0.0

On your host machine:

	$ prove -c conf/test/prove.yml -t remote.vagrant cmd 'echo hello world'
