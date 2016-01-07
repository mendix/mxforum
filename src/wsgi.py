import django.core.handlers.wsgi

_application = django.core.handlers.wsgi.WSGIHandler()


def application(environ, start_response):
    environ['HTTPS'] = 'on'
    return _application(environ, start_response)
