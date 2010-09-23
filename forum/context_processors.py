from django.conf import settings
def mxid_url(request):
	return {'mxid_url' : settings.MXID_URL}

def mxwww_url(request):
	return {'mxwww_url' : settings.MXWWW_URL}

def mxappstore_url(request):
	return {'mxappstore_url' : settings.MXAPPSTORE_URL}
