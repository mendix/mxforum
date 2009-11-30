from django.conf import settings
from django.contrib.auth.models import User
from base64 import b64encode
import urllib
from hashlib import sha256
import logging
from django.utils import simplejson
import sys
 
class SSOModelBackend(object):

    def authenticate_token(self, request, token):
        original = "%s%s" % (request.META['REMOTE_ADDR'],  request.META['HTTP_USER_AGENT'])
        sys.stderr.write("sysdtr original %s " % original)
        sys.stderr.flush()
        logging.error("original %s " % original)
        hashed = b64encode(sha256(original).digest())
        requestdata = urllib.urlencode([('token', token), ('a', 'forum'), ('client', hashed)])
        sys.stderr.write("going to send requestdata %s " % requestdata)
        logging.error("going to send requestdata %s " % requestdata)
        u = urllib.urlopen("%s/mxid/validatetoken" % settings.MXID_URL, requestdata)

        response = simplejson.decode(u.read())
        sys.stderr.write("called, decoded and closed stream. result %s" % response)
        logging.error("called, decoded and closed stream. result %s" % response)
        if (response["valid"] == True):
            return response["username"]
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request=None, token=None):
        username = self.authenticate_token(request=request, token=token)
        if username is not None:
            try:
                user = User.objects.get(username=username)
                return user
            except User.DoesNotExist:
                return None
        else:
            return None
