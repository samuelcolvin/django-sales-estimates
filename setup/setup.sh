#!/bin/bash

# script to setup the python enviroment for django
# you many also need to run:
# sudo apt-get install libmysqlclient-dev python-dev libapache2-mod-wsgi
# sudo apt-get install  libmysqlcppconn-dev
# sudo apt-get install libboost-python-dev python-dev
rm -r ../env
virtualenv ../env
../env/bin/pip install -r requirements.txt

