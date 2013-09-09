"""
WSGI config for markets_django project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "viewer.settings")

from django.core.handlers.wsgi import WSGIHandler
import settings

class WSGIHandler(WSGIHandler):
    def __call__(self, environ, start_response):
#         print "before SCRIPT_NAME = '%s', PATH_INFO = '%s'" % (environ['SCRIPT_NAME'], environ['PATH_INFO'])
        
        if settings.ON_SERVER:
            if environ['PATH_INFO'].startswith('/' + settings.SCRIPT_NAME):
                environ['PATH_INFO'] = environ['PATH_INFO'].replace(settings.SCRIPT_NAME, '')
            else:
                transfer = environ['SCRIPT_NAME'].replace(settings.SCRIPT_NAME, '')
                environ['PATH_INFO'] = transfer + environ['PATH_INFO']
            environ['SCRIPT_NAME'] = '/' + settings.SCRIPT_NAME
        
#         print "after SCRIPT_NAME = '%s', PATH_INFO = '%s'" % (environ['SCRIPT_NAME'], environ['PATH_INFO'])
        return super(WSGIHandler, self).__call__(environ, start_response)


# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.

#CHANGED BY ME: {
# WAS from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()
application = WSGIHandler()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
