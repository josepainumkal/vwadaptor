#!/bin/sh

#remove previous db
rm -rf migrations
rm -rf dev.db

#create new db
python manage.py db init
python manage.py db migrate
python manage.py db upgrade