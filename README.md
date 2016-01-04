# Prove

Prove is a configuration management system, similar to Puppet, Chef, Ansible and Salt.

## Installation

Make sure `$HOME/.local/bin` is in your `$PATH`:

	$ pip install --user prove

Alternatively, if you're not concerned about using sudo:

	$ sudo pip install prove

## Development

For development and testing, use a virtualenv:

	$ cd /path/to/prove
	$ virtualenv -p python3 .
	$ source bin/activate
	$ pip install -e .
	$ pip install -r requirements_dev.txt

Tests are ran with pytest:

	$ py.test

Linting is done with pylint:

	$ pylint prove
