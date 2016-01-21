python health_dummie.py & 
celery -A forum.tasks worker --loglevel=info
