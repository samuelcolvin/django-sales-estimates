import os
import sys

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

ON_SERVER = False #'linux' in sys.platform.lower()
if ON_SERVER:
	DEBUG = False
else:
	DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (('Samuel Colvin', 'S@muelColvin.com'),)

MANAGERS = ADMINS

if ON_SERVER:
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.mysql',
	        'NAME': 'scolvin_childsfarm',
	        'USER': 'scolvin',
	        'PASSWORD': 'Cg7GIzAq',
	        'HOST': '',
	        'PORT': '',
	    }
	}
else:
	USE_LOCAL_MYSQL = True
	if USE_LOCAL_MYSQL:
		DATABASES = {
		    'default': {
		        'ENGINE': 'django.db.backends.mysql',
		        'NAME': 'salesestimates',
		        'USER': 'sales-user',
		        'PASSWORD': '',
		        'HOST': '127.0.0.1',
		        'PORT': '3306',
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

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.sites.djangoeurope.com']

TIME_ZONE = 'Europe/London'

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

TEMPLATE_CONTEXT_PROCESSORS =(
	"django.contrib.auth.context_processors.auth",
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
    'SkeletalDisplay.middleware.LoginRequiredMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (os.path.join(SITE_ROOT, 'templates'),
				os.path.join(SITE_ROOT, 'SkeletalDisplay/templates'))

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	
    'django.contrib.admin',
    'django.contrib.admindocs',
    'rest_framework',
	'django_tables2',
	'bootstrapform',
    'HotDjango',
    'SkeletalDisplay',
    'SalesEstimates',
    'Imex',
    'django_extensions',
    'south'
)

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
DISPLAY_APPS = ['SalesEstimates', 'SkeletalDisplay']
HOT_PERMITTED_GROUPS = 'all'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
PAGE_BASE = 'page_base.html'
SK_VIEW_SETTINGS ={'viewname': 'process', 'args2include': [False, True], 'base_name': 'Process'}

SITE_TITLE = 'childsfarm'
TOP_MENU = [{'url': 'process', 'name': 'Process'},
 			{'url': 'imex_import', 'name': 'Import'}, 
			{'url': 'imex_export', 'name': 'Export'}]
LOGIN_REDIRECT_URL = '/'
INTERNAL_IPS = ('127.0.0.1',)

# HotDjango settings
# HOT_ID_IN_MODEL_STR = True

#ExcelImportExport Settings
IMEX_APP = 'SalesEstimates'

# Sales Estimates settings

# number of weeks demands are grouped into
DEMAND_GROUPING = 13
# general constant lead time in weeks
GENERAL_LEAD_TIME = 14

#sales period length on months
SALES_PERIOD_START_DATE = '2014-01-01'
SALES_PERIOD_FINISH_DATE = '2016-01-01'
