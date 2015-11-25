from __future__ import absolute_import
import datetime
import redis
import json
from forum.flylogger import flog
from suds.client import Client
from settings import EVENTREG_ENABLED, EVENTREG_LOCATION, EVENTREG_USER, EVENTREG_PASS
from celery import Celery
from django.conf import settings as djsettings

ALAN_ACTIVE = False
client = None

try:
    client = Client(EVENTREG_LOCATION)
    ALAN_ACTIVE = True
    app = Celery('forum')
    flog("WSDL was loaded successfully")
except:
    ALAN_ACTIVE = False
    flog("ALAN: Could NOT open platform analytics WSDL at location: (%s)." % EVENTREG_LOCATION)

if client:
    # Using a string here means the worker will not have to
    # pickle the object when using Windows.
    app.config_from_object('django.conf:settings')
    app.autodiscover_tasks(lambda: djsettings.INSTALLED_APPS)
    
    @app.task(bind=True, max_retries=20)
    def send_event(self, _event):
        if EVENTREG_ENABLED:
            if ALAN_ACTIVE:
                try:
                    event = json.loads(_event)
                    
                    client.set_options(soapheaders={'authentication' : {'username': EVENTREG_USER, 'password': EVENTREG_PASS}})
                    client.service.RegisterEvent(event)
            
                except Exception as e:
                    flog("ALAN: Error whilst trying to register event (%s)" % e)
                    raise self.retry(exc=e, countdown=60 * 10)
            else:
                flog("ALAN: Failed to send event, ALAN is NOT active.")
        else:
            flog("ALAN: Event registration is DISABLED.")
else:
    ALAN_ACTIVE = False
    flog("ALAN: Send_event task not registered as SUDS client is not loaded.")