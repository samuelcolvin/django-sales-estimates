from django.conf.urls import patterns, include, url
import settings
import SalesEstimates.views as views
# import ExcelImportExport.forms as imex_forms

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^hot/', include('HotDjango.urls')),
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^', include('SkeletalDisplay.urls')),
    url(r'^imex/', include('Imex.urls')),
    url(r'^process$', views.SetupDisplayModel.as_view(), name='process'),
    url(r'^process/(?P<model>\w+)$', views.SetupDisplayModel.as_view(), name='process'),
    url(r'^process/(?P<model>\w+)/(?P<id>\d+)$', views.SetupDisplayItem.as_view(), name='process'),
    url(r'^generate$', views.Generate.as_view(), name='generate'),
    url(r'^generate/(?P<command>\w+)$', views.Generate.as_view(), name='generate'),
    url(r'^results$', views.ResultsDisplayModel.as_view(), name='results'),
    url(r'^results/(?P<model>\w+)$', views.ResultsDisplayModel.as_view(), name='results'),
    url(r'^results/(?P<model>\w+)/(?P<id>\d+)$', views.ResultsDisplayItem.as_view(), name='results'),
    
#     url(r'^import$', 'ExcelImportExport.forms.upload', name='import'),
#     url(r'^export$', imex_forms.Export.as_view(), name='export'),
#     url(r'^export/(?P<command>\w+)$', imex_forms.Export.as_view(), name='export'),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
