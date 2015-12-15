import datetime
import settings
import os

def flog(string):
    path = ''
    # Windows
    try:
        if os.name == 'nt':
            path = os.path.abspath(os.path.join('src', 'forum.log'))
        else:
            path = '%s/forum.log' % settings.SITE_SRC_ROOT
    
        with open(path, 'a+') as f:
            f.write( "[%s] %s\n\n" % (datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"), string))
            
    except:
        pass