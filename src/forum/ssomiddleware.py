from django.http import HttpResponseRedirect
import settings
from forum.login_views import mxid_login
from forum.login_views import login_redirect
from forum.views import users_feed
from forum.views import questions_feed
from forum.views import error


class CheckMxIdCookie():


	def process_view(self, request, view_func, view_args, view_kwargs):
		if view_func == mxid_login:
			return None

		if view_func == error:
			return None

		if view_func == login_redirect:
			return None
		
		if view_func == users_feed:
			return None

		if view_func == questions_feed:
			return None

		if has_cookie(request): 
			if not request.user.is_authenticated():
				return HttpResponseRedirect("%s/mxid/login?a=forum&cont=%s" % (settings.MXID_URL, request.get_full_path()))
		return None

def has_cookie(request):
	if not 'MXID_ENABLED' in request.COOKIES.iterkeys(): 
		return False

	return request.COOKIES['MXID_ENABLED'].lower() == 'true'
