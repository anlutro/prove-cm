#!/bin/sh

# apt-get install devscripts debhelper python3-all

root=$(dirname $0)
$root/bin/python ./setup.py --command-packages=stdeb.command bdist_deb
rm prove-*.tar.gz
