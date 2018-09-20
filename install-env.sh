#!/bin/bash

wget https://nodejs.org/dist/v8.12.0/node-v8.12.0-linux-x64.tar.xz
tar xf node-v8.12.0-linux-x64.tar.xz
mv node-v8.12.0-linux-x64 env
virtualenv --python=`which python3` env

. env/bin/activate
pip3 install django
pip3 install numpy
pip3 install simplejson h5py scipy
