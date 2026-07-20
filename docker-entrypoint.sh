#!/bin/bash
python manage.py migrate &&
python manage.py collectstatic --no-input &&
exec gunicorn online_store.wsgi:application --bind 0.0.0.0:8000
