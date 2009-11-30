from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
import settings

def mxid_login(request, token, email, redirect=settings.LOGIN_REDIRECT_URL):
    user = authenticate(request=request, token=token)
    if user is not None:
        if user.is_active:
            login(request, user)
            print "login ok, redirecting to %s" % redirect
            return HttpResponseRedirect(redirect)
        else:
            return HttpResponseRedirect("/error?error=User%20isnt%20active")
    else:
        return HttpResponseRedirect("/error?error=User%20doesnt%20have%20an%20account%20for%20the%20forum")

def login_redirect(request):
	if 'next' in request.GET:
		return HttpResponseRedirect("%s/mxid/login?a=forum&cont=%s" % (settings.MXID_URL, request.GET['next']))
        
	return HttpResponseRedirect("%s/mxid/login?a=forum" % settings.MXID_URL)
