#!/bin/bash

if [ ! -f users.txt ]
then
    echo "Using test users"
    cp test-users.txt users.txt
fi
rm web/migrations/*.py
./manage.py makemigrations web
rm db.sqlite3
./manage.py migrate
./manage.py setup
#./manage.py import 
