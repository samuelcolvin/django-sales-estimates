from django.conf.urls import patterns, include, url
import settings
import SalesEstimates.views as views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^hot/', include('HotDjango.urls')),
    url(r'^', include('SkeletalDisplay.urls')),
    url(r'^process$', views.SetupIndex.as_view(), name='process'),
    url(r'^process/(?P<model>\w+)$', views.SetupDisplayModel.as_view(), name='process'),
    url(r'^process/(?P<model>\w+)/(?P<id>\d+)$', views.SetupDisplayItem.as_view(), name='process'),
    url(r'^generate1$', views.GenerateCUSKI.as_view(), name='generate_cskui'),
    url(r'^generate1/(?P<command>\w+)$', views.GenerateCUSKI.as_view(), name='generate_cskui'),
    url(r'^delete_all_cskui$', 'SalesEstimates.views.delete_all_cskui', name='delete_all_cskui'),
    url(r'^process_alter$', views.AlterDisplayModel.as_view(), name='process_alter'),
    url(r'^process_alter/(?P<model>\w+)$', views.AlterDisplayModel.as_view(), name='process_alter'),
    url(r'^process_alter/(?P<model>\w+)/(?P<id>\d+)$', views.AlterDisplayItem.as_view(), name='process_alter'),
    
    url(r'^upload','ExcelImportExport.forms.upload', name='upload'),
    url(r'^download','ExcelImportExport.forms.download', name='download'),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)