#!/usr/bin/env bash
set -o errexit

pip install -r requirements/production.txt


# 1. Install dependencies
pip install -r requirements/base.txt

# 2. Run database migrations
python manage.py migrate --settings=config.settings.production

# 3. Collect static files
python manage.py collectstatic --noinput --settings=config.settings.production

# 4. Create superuser (optional)
python manage.py createsuperuser --settings=config.settings.production

# 5. Check production readiness
python manage.py check_production --settings=config.settings.production
