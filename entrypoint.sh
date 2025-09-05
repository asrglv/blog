#!/bin/bash
echo "Starting collect static files..."
python manage.py collectstaticfiles

echo "Starting migrate data.."
python manage.py migrate

echo "Starting load data..."
python manage.py loaddata data.json

echo "Starting serverl.."
exec "$@"
