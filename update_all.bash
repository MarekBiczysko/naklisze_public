#!/bin/bash

source sklepenv/bin/activate
git reset --hard HEAD
git pull
cd src
python3.6 manage.py collectstatic --noinput --clear
python3.6 manage.py migrate
service nginx restart
supervisorctl restart sklep
