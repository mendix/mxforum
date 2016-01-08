from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
import settings
import urllib


def mxid_login(request, token, redirect=settings.LOGIN_REDIRECT_URL):
    user = authenticate(request=request, token=token)
    if user is not None:
        if user.is_active:
            login(request, user)
            redirect = urllib.unquote(redirect)
            if len(redirect) > 0 and redirect[0] == "/":
                redirect = redirect[1:]
            return HttpResponseRedirect("%s/%s" % (settings.MY_URL, redirect))
        else:
            return HttpResponseRedirect("/error?error=User+isnt+active")
    else:
        return HttpResponseRedirect(
            "/error?error=User+doesnt+have+an+account+for+the+forum"
        )


def login_redirect(request):
    if 'next' in request.GET:
        return HttpResponseRedirect(
            "%s/mxid/login?a=forum&cont=%s"
            % (settings.MXID_URL, request.GET['next'])
        )

    return HttpResponseRedirect("%s/mxid/login?a=forum" % settings.MXID_URL)
