#!/bin/bash
sleep 2
python manage.py migrate --noinput
if [ "$WEBPING_ENV" != "prod" ]; then
  python manage.py loaddata dev_data.json
fi

