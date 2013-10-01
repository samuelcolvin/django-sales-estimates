from django.conf.urls import patterns, include, url
import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^hot/', include('HotDjango.urls')),
    url(r'^', include('SkeletalDisplay.urls')),
    url(r'^upload','ExcelImportExport.forms.upload', name='upload'),
    url(r'^download','ExcelImportExport.forms.download', name='download'),
    url(r'^generate', 'SalesEstimates.worker.generate', name='generate'),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)