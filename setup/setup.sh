#!/bin/bash

# script to setup the python enviroment for django
# you many also need to run:
# sudo apt-get install libmysqlclient-dev python-dev libapache2-mod-wsgi
rm -r ../env
virtualenv ../env
../env/bin/pip install -r requirements.txt

