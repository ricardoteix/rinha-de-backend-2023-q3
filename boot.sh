#!/bin/sh

exec gunicorn -b :80 --timeout 60 --workers=5 --access-logfile - --error-logfile - app:app;