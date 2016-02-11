import os
import os.path
import json

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

TEMPLATE_DEBUG = DEBUG

SITE_SRC_ROOT = os.getcwd()


INTERNAL_IPS = ('0.0.0.0',)

DEBUG_TOOLBAR_PANELS = (
)
DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False
}

LOGIN_URL = '/accounts/login/'

# system will send admins email about error stacktrace if DEBUG=False
ADMINS = (
    ('Mendix', 'webmaster@mendix.com'),
)

MANAGERS = ADMINS

SERVER_EMAIL = 'webmaster@mendix.com'
DEFAULT_FROM_EMAIL = 'webmaster@mendix.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = '[world.mendix.com]'
#  TODO: use service provided by PWS
EMAIL_HOST = '10.140.10.1'
# EMAIL_PORT='587'
EMAIL_PORT = '25'
EMAIL_USE_TLS = False


# CELERY SETTINGS
# These are automatically picked up by celery
if os.environ.get('VCAP_SERVICES'):
    redis_credentials = json.loads(
        os.environ['VCAP_SERVICES']
    )['rediscloud'][0]['credentials']
    BROKER_URL = 'redis://:{password}@{host}:{port}/0'.format(
        host=redis_credentials['hostname'],
        password=redis_credentials['password'],
        port=redis_credentials['port'],
    )

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = 'templates/upfiles/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://127.0.0.1:7777/upfiles/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    # 'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'forum.ssomiddleware.CheckMxIdCookie',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'forum.context_processors.mxid_url',
    'forum.context_processors.mxappstore_url',
    'forum.context_processors.mxsprintr_url',
    'forum.context_processors.mxdevsite_url',
    'forum.context_processors.mxconfl_url',
    'forum.context_processors.mxacademy_url',
    'forum.context_processors.modelshare_url',
    'forum.context_processors.gettingstarted_url',
    'forum.context_processors.myprofile_url',
    'forum.context_processors.mxwww_url',
    'forum.context_processors.footer_json_mxwww_url',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace(
        '\\', '/'
    ),
)

FILE_UPLOAD_TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tmp').replace(
    '\\',
    '/'
)
FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# for user upload
ALLOW_FILE_TYPES = ('.jpg', '.jpeg', '.gif', '.bmp', '.png', '.tiff')
# unit byte
ALLOW_MAX_FILE_SIZE = 1024 * 1024

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'forum',
)

AUTHENTICATION_BACKENDS = (
    'forum.ssoauth.SSOModelBackend',
)
LOGIN_REDIRECT_URL = '/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


if os.environ.get('VCAP_SERVICES'):
    db_credentials = json.loads(
        os.environ.get('VCAP_SERVICES')
    )['cleardb'][0]['credentials']
    DATABASE_ENGINE = 'mysql'
    DATABASE_NAME = db_credentials['name']
    DATABASE_HOST = db_credentials['hostname']
    DATABASE_PORT = db_credentials['port']
    DATABASE_USER = db_credentials['username']
    DATABASE_PASSWORD = db_credentials['password']
    DATABASE_OPTIONS = {'ssl':
                        {'ca': '/%s/%s/%s' % (os.getcwd(), 'mysql', 'ca'),
                        'cert': '/%s/%s/%s' % (os.getcwd(), 'mysql', 'cert'),
                        'key': '/%s/%s/%s' % (os.getcwd(), 'mysql', 'key')}}

SECRET_KEY = os.environ.get('SECRET_KEY')
LOGIN_REDIRECT_URL = '/'
MY_HOST = os.environ.get('MY_HOST')
MY_URL = "https://%s/" % MY_HOST
MXID_URL = os.environ.get('MXID_URL')
MXWWW_URL = os.environ.get('MXWWW_URL')
MXDEVSITE_URL = os.environ.get('MXDEVSITE_URL')
MXSPRINTR_URL = os.environ.get('MXSPRINTR_URL')
MXAPPSTORE_URL = os.environ.get('MXAPPSTORE_URL')
MXSPRINTR_URL = os.environ.get('MXSPRINTR_URL')
MXDEVSITE_URL = os.environ.get('MXDEVSITE_URL')
MXCONFL_URL = os.environ.get('MXCONFL_URL')
MXACADEMY_URL = os.environ.get('MXACADEMY_URL')
MODELSHARE_URL = os.environ.get('MODELSHARE_URL')
GETTINGSTARTED_URL = os.environ.get('GETTINGSTARTED_URL')
FOOTER_JSON_MXWWW_URL = os.environ.get('FOOTER_JSON_MXWWW_URL')
MYPROFILE_URL = os.environ.get('MYPROFILE_URL')
WEBSERVICE_PASSWORD = os.environ.get('WEBSERVICE_PASSWORD')

EVENTREG_WSDL = 'file:///%s/%s' % (os.getcwd(), 'EventsRegistration.wsdl')

EVENTREG_LOCATION = os.environ.get('EVENTREG_LOCATION')
EVENTREG_USER = os.environ.get('EVENTREG_USER')
EVENTREG_PASS = os.environ.get('EVENTREG_PASS')
EVENTREG_ENABLED = os.getenv('EVENTREG_ENABLED', 'false').lower() == 'true'

try:
    from local_settings import *
except ImportError, exp:
    pass
