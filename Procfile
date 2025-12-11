web: gunicorn wsgi:app --workers 1 --threads 2 --timeout 300 --max-requests 1000 --max-requests-jitter 50 --worker-class gthread --worker-tmp-dir /dev/shm
