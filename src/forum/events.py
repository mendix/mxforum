import datetime
import redis
import json
from logging import log
from suds.client import Client
from settings import EVENTREG_LOCATION, EVENTREG_USER, EVENTREG_PASS, REDIS_LOC, REDIS_PASS
from celery import Celery

ALAN_ACTIVE = False

try:
    client = Client(EVENTREG_LOCATION)
    ALAN_ACTIVE = True
    app = Celery('events', broker='redis://:%s@%s//' % (REDIS_PASS, REDIS_LOC))
except:
    ALAN_ACTIVE = False
    log("ALAN: Could NOT open platform analytics WSDL at location: (%s)." % EVENTREG_LOCATION)
    log("ALAN: THIS MEANS NO EVENTS WILL BE SENT.")

@app.task
def send_event(_event):
    if ALAN_ACTIVE:
        try:
            event = json.loads(_event)
            
            client.set_options(soapheaders={'authentication' : {'username': EVENTREG_USER, 'password': EVENTREG_PASS}})
            log("ALAN: Stub for event sending with type: %s ", event.EventType)
            client.service.RegisterEvent(eventargs)
    
        except e:
            log("ALAN: Error whilst trying to register event (%s)" % e.message)
            raise
    else:
        log("ALAN: Failed to send event, ALAN is NOT active.")