from django.conf.urls import patterns, include, url
import settings

import SkeletalDisplay.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = SkeletalDisplay.urls.urlpatterns

urlpatterns += patterns('',
	url(r'^admin/', include(admin.site.urls), name='admin'),)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)