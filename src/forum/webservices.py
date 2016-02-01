#
# WSDL fun
# 

from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from soaplib.serializers import primitive as soap_types
from forum.models import *

from django.http import HttpResponse

import sys
from settings import WEBSERVICE_PASSWORD as ws_password

class DjangoSoapApp(SimpleWSGISoapApp):

    def __call__(self, request):
        django_response = HttpResponse()
        def start_response(status, headers):
            status, reason = status.split(' ', 1)
            django_response.status_code = int(status)
            for header, value in headers:
                django_response[header] = value
        from settings import MY_HOST
        request.META['HTTP_HOST'] = MY_HOST

        response = super(SimpleWSGISoapApp, self).__call__(request.META, start_response)
        sys.stderr.write("going to send response %s" % response)
        sys.stderr.flush()
        django_response.content = "\n".join(response)

        return django_response

# import soapmethod, soap_types

class UserImportService(DjangoSoapApp):

    __tns__ = 'http://www.mendix-ns.org/soap/'


    @soapmethod(soap_types.String, soap_types.String, soap_types.String, soap_types.String, soap_types.String, _returns=soap_types.Boolean)
    def set_user(self, _service_password, _email, _name, _about, _website):
        from settings import DEBUG
		# check authentication:
        if not _service_password == ws_password:
            if DEBUG==True:
                sys.stderr.write("wrong password")
                sys.stderr.flush()
            return 0

        u, created = User.objects.get_or_create(username=_email)
        if DEBUG==True:
            sys.stderr.write("MXforum WEBSERVICES set_user called with params email: %s, name: %s, about %s, website %s" % (_email, _name, _about, _website))
            if created:
                sys.stderr.write("Created user %s" % u)
            else:
                sys.stderr.write("Found user %s" % u)
            sys.stderr.flush()

        u.username   = _email
        u.real_name  = _name
        if _about is not None:
            u.about = _about
        if _website is not None:
            u.website = _website	
        u.set_password("sapperdeflap")
        u.save()
        return 1

user_import_service = UserImportService()

# New Soap version that also sends over the OpenID

class UserImportService2(DjangoSoapApp):

    __tns__ = 'http://www.mendix-ns.org/soap/'


    @soapmethod(soap_types.String, soap_types.String, soap_types.String, soap_types.String, soap_types.String, soap_types.String, _returns=soap_types.Boolean)
    def set_user(self, _service_password, _email, _name, _about, _website, _openid):
        from settings import DEBUG
		# check authentication:
        if not _service_password == ws_password:
            if DEBUG==True:
                sys.stderr.write("wrong password")
                sys.stderr.flush()
            return 0

        u, created = User.objects.get_or_create(username=_email)
        if DEBUG==True:
            sys.stderr.write("MXforum WEBSERVICES set_user called with params openid: %s, email: %s, name: %s, about %s, website %s" % (_openid, _email, _name, _about, _website))
            if created:
                sys.stderr.write("Created user %s" % u)
            else:
                sys.stderr.write("Found user %s" % u)
            sys.stderr.flush()

        u.username   = _email
        u.openid = _openid
        u.real_name  = _name
        if _about is not None:
            u.about = _about
        if _website is not None:
            u.website = _website	
        u.set_password("sapperdeflap")
        u.save()
        return 1

user_import_service2 = UserImportService2()

# Webservice to send alternative point values for users

class UserPointsUpdateService(DjangoSoapApp):

    __tns__ = 'http://www.mendix-ns.org/soap/'


    @soapmethod(soap_types.String, soap_types.String, soap_types.Integer, soap_types.Integer, soap_types.Integer, _returns=soap_types.Boolean)
    def update_points(self, _service_password, _openid, _totalpts, _forumpts, _level):
        from settings import DEBUG
		# check authentication:
        if not _service_password == ws_password:
            if DEBUG==True:
                sys.stderr.write("wrong password")
                sys.stderr.flush()
            return 0
        
        try:
            u = User.objects.get(openid=_openid)
        except:
            print "Could not find user for openid: %s" % _openid
            return 0
            
        if DEBUG==True:
            sys.stderr.write("MXforum WEBSERVICES update_points called with params openid: %s, _totalpts: %s, _forumpts: %s, _level: %s" % (_openid, _totalpts, _forumpts, _level))
            sys.stderr.flush()

        u.totalpts = _totalpts
        u.forumpts = _forumpts
        u.level = _level
        u.save()
        return 1

user_points_update_service = UserPointsUpdateService()