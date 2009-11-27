from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
import settings

def mxid_login(request, token, email, redirect):
    user = authenticate(request=request, token=token)
    if user is not None:
        if user.is_active:
            login(request, user)
            print "login ok, redirecting to %s" % redirect
            return HttpResponseRedirect(redirect)
        else:
            return HttpResponseRedirect("%s/argh" % settings.MXID_URL)
    else:
        return HttpResponseRedirect("%s/argh" % settings.MXID_URL)

def login_redirect(request):
	if 'next' in request.GET:
		return HttpResponseRedirect("%smxid/login?a=forum&cont=%s" % (settings.MXID_URL, request.GET['next']))
        
	return HttpResponseRedirect("%smxid/login?a=forum" % settings.MXID_URL)
