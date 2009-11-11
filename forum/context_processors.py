def mxid_url(request):
	from django.conf import settings
	return {'mxid_url' : settings.MXID_URL}
