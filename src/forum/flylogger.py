import datetime
import settings

def flog(string):
    path = '%s/forum.log' % settings.SITE_SRC_ROOT
    with open(path, 'a+') as f:
        f.write( "[%s] %s\n\n" % (datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"), string))
