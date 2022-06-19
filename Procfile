release: python manage.py migrate
web: gunicorn FakeSchema.wsgi & celery -A FakeSchema worker -l info