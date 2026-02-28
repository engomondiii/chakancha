#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations (optional - only if using PostgreSQL)
# python manage.py migrate --noinput