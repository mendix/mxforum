# soaplib_handler.py

from soaplib.wsgi_soap import SimpleWSGISoapApp 
from soaplib.service import soapmethod 
from soaplib.serializers import primitive as soap_types 
import StringIO

from django.http import HttpResponse

class DumbStringIO(StringIO.StringIO): 
    def read(self, n): 
        return self.getvalue()

class DjangoSoapApp(SimpleWSGISoapApp):

def __call__(self, request):

    django_response = HttpResponse()
    def start_response(status, headers):
        status, reason = status.split(' ', 1)
        django_response.status_code = int(status)
        for header, value in headers:
            django_response[header] = value

    environ = request.META.copy()
    body = ''.join(['%s=%s' % v for v in request.POST.items()])
    environ['CONTENT_LENGTH'] = len(body)
    environ['wsgi.input'] = DumbStringIO(body)
    environ['wsgi.multithread'] = False

    response = super(DjangoSoapApp, self).__call__(environ, start_response)

    django_response.content = "\n".join(response)

    return django_response

