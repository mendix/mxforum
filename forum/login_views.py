from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
import settings

def mxid_login(request, token, email):
    user = authenticate(request=request, token=token)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect("%s/argh" % settings.MXID_URL)
    else:
        return HttpResponseRedirect("%s/argh" % settings.MXID_URL)
