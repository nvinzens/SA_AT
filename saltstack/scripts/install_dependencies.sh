#!/bin/bash
sudo apt-get update && sudo apt-get install -y --force-yes libssl-dev libffi-dev python-dev python-cffi
sudo apt-get install -y python-pip python-dev build-essential
sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv
sudo pip install setuptools
sudo pip install --upgrade setuptools
sudo pip install napalm
