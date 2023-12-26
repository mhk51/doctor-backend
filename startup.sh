# daphne -p 8000 --bind 0.0.0.0 backend.asgi:application
# gunicorn backend.wsgi:application --access-logfile '-' --error-logfile '-'
daphne -p 8000 --bind 0.0.0.0 backend.asgi:application 

# nohup python scheduler.py &
