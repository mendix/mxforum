import tasks
import os
import settings

import sys
sys.path.append('%s/src/' % settings.SITE_SRC_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
