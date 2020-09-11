#!/bin/sh
sleep 2
export C_FORCE_ROOT="true"
celery -A webping beat -l info
