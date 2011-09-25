import os, sys
import site

site.addsitedir('/opt/mxforum/venv/lib/python2.5/site-packages')

sys.path.append('/opt/mxforum/src/')
sys.path.append('/opt/mxforum/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    if environ['wsgi.url_scheme'] == 'https':
        environ['HTTPS'] = 'on'
    return _application(environ, start_response)
from repoze.profile.profiler import AccumulatingProfileMiddleware
application = AccumulatingProfileMiddleware(
               application,
               log_filename='/tmp/mxforum_profiler.log',
               cachegrind_filename='/tmp/mxforum_cachegrind',
               discard_first_request=True,
               flush_at_shutdown=True,
               path='/__profile__'
              )
