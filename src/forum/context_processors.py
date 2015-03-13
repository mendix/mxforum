from django.conf import settings
def mxid_url(request):
	return {'mxid_url' : settings.MXID_URL}

def mxwww_url(request):
	return {'mxwww_url' : settings.MXWWW_URL}

def footer_json_mxwww_url(request):
	return {'footer_json_mxwww_url' : settings.FOOTER_JSON_MXWWW_URL}

def mxappstore_url(request):
	return {'mxappstore_url' : settings.MXAPPSTORE_URL}

def mxsprintr_url(request):
	return {'mxsprintr_url' : settings.MXSPRINTR_URL}

def mxdevsite_url(request):
	return {'mxdevsite_url' : settings.MXDEVSITE_URL}

def mxconfl_url(request):
	return {'mxconfl_url' : settings.MXCONFL_URL}

def mxacademy_url(request):
	return {'mxacademy_url' : settings.MXACADEMY_URL}

def modelshare_url(request):
	return {'modelshare_url' : settings.MODELSHARE_URL}
