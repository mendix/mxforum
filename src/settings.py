# Django settings for lanai project.
import os.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_SRC_ROOT = '/opt/mxforum/src/'
#David Cramer debug toolbar
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_PANELS = (
)

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS":False
}


#for OpenID auth
ugettext = lambda s: s
LOGIN_URL = '/%s%s' % (ugettext('accounts/'), ugettext('login/'))

#system will send admins email about error stacktrace if DEBUG=False
ADMINS = (
    ('Mendix', 'webmaster@mendix.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

DATABASE_NAME = 'mxforum'             # Or path to database file if using sqlite3.
DATABASE_USER = 'mxforum'             # Not used with sqlite3.
DATABASE_PASSWORD = '1'         # Not used with sqlite3.

SECRET_KEY = 'nottellingyou' # change in local_settings

SERVER_EMAIL = 'webmaster@mendix.com'
DEFAULT_FROM_EMAIL = 'webmaster@mendix.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = '[world.mendix.com]'
EMAIL_HOST='10.140.10.1'
# EMAIL_PORT='587'
EMAIL_PORT='25'
EMAIL_USE_TLS=False

EVENTREG_LOCATION=''
EVENTREG_USER=''
EVENTREG_PASS=''




# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/WET'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'en-us'
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
#     'django.template.loaders.eggs.load_template_source',
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
	'forum.context_processors.mxwww_url',
	'forum.context_processors.footer_json_mxwww_url',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)

FILE_UPLOAD_TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tmp').replace('\\','/')
FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
 "django.core.files.uploadhandler.TemporaryFileUploadHandler",)
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
SESSION_EXPIRE_AT_BROWSER_CLOSE=True


try:
    from local_settings import *
except ImportError, exp:
    pass

