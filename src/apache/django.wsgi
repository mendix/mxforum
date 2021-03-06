import os, sys
sys.path.append('/opt/mxforum/src/')
sys.path.append('/opt/mxforum/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    if environ['wsgi.url_scheme'] == 'https':
        environ['HTTPS'] = 'on'
    return _application(environ, start_response)

