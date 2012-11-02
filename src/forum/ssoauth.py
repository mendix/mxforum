from django.conf import settings
from django.contrib.auth.models import User
from base64 import b64encode
import urllib
from hashlib import sha256
from django.utils import simplejson
 
class SSOModelBackend(object):

    def authenticate_token(self, request, token):
        header_keys = ['HTTP_USER_AGENT', 'HTTP_ACCEPT_CHARSET', 'HTTP_ACCEPT_ENCODING', 'HTTP_ACCEPT_LANGUAGE']
        user_agent_tokens = []
        for header_key in header_keys:
            if header_key in request.META:
                user_agent_tokens.append(request.META[header_key])
            else:
                user_agent_tokens.append('null')
        
        user_agent = "".join(user_agent_tokens)
        hashed = b64encode(sha256(user_agent).digest())
        requestdata = urllib.urlencode([('token', token), ('a', 'forum'), ('client', hashed)])
        u = urllib.urlopen("%s/mxid/validatetoken" % settings.MXID_URL, requestdata)

        response = simplejson.load(u)
        u.close()
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
