import os
import sys

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

ON_SERVER = 'linux' in sys.platform.lower()
if ON_SERVER:
	DEBUG = True
else:
	DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (('Samuel Colvin', 'S@muelColvin.com'),)

MANAGERS = ADMINS

if ON_SERVER:
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.mysql',
	        'NAME': 'db_name',
	        'USER': 'username',
	        'PASSWORD': 'password',
	        'HOST': '',
	        'PORT': '',
	    }
	}
else:
	DATABASES = {
 	    'default': {
 	        'ENGINE': 'django.db.backends.sqlite3',
 	        'NAME': os.path.join(SITE_ROOT, 'sqlite.db'),
 	        'USER': '',
 	        'PASSWORD': '',
 	        'HOST': '',
 	        'PORT': '',
 	    }
 	}

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
# changed by me
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
MEDIA_URL = '/media/'
MEDIA_RELATIVE_ROOT = 'media'
MEDIA_ROOT = os.path.join(SITE_ROOT, MEDIA_RELATIVE_ROOT)
if ON_SERVER:
 	SCRIPT_NAME = ''
 	FORCE_SCRIPT_NAME = ''

STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'tr@-fv7^uv5n7j9c2f!kia+dyrxij_$o8=_alu+$z!b^7$ka-q'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS =("django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.core.context_processors.tz",
	"django.contrib.messages.context_processors.messages",
	'django.core.context_processors.request')

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (os.path.join(SITE_ROOT, 'templates'),
				os.path.join(SITE_ROOT, 'SkeletalDisplay/templates'))

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'se.SalesEstimates',
    'se.SkeletalDisplay',
    'se.UploadedFiles',
	'django_tables2',
]

if not ON_SERVER:
	INSTALLED_APPS.append('south')
INSTALLED_APPS = tuple(INSTALLED_APPS)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# added by me:

CUSTOM_DATE_FORMAT = '%Y-%m-%d'
CUSTOM_DT_FORMAT = '%Y-%m-%d %H:%M:%S %Z'
CUSTOM_SHORT_DT_FORMAT = '%y-%m-%d_%H %M'
DATETIME_FORMAT = 'Y-m-d H:i:s'
SHORT_DATETIME_FORMAT = DATETIME_FORMAT

#Skeletal Dispaly Settings
DISPLAY_APPS = ['SalesEstimates']

#Sales Estimates

#sales period length on months
SALES_PERIOD_START_DATE = '2013-01-01'
SALES_PERIOD_FINISH_DATE = '2020-01-01'
SALES_PERIOD_LENGTH = 3