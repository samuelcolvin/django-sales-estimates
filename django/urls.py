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
    url(r'^setup$', views.SetupDisplayModel.as_view(), name='setup'),
    url(r'^setup/(?P<model>\w+)$', views.SetupDisplayModel.as_view(), name='setup'),
    url(r'^setup/(?P<model>\w+)/(?P<id>\d+)$', views.SetupDisplayItem.as_view(), name='setup'),
    url(r'^generate$', views.Generate.as_view(), name='generate'),
    url(r'^results$', views.ResultsDisplayModel.as_view(), name='results'),
    url(r'^charts$', views.Charts.as_view(), name='charts'),
    url(r'^results/(?P<model>\w+)$', views.ResultsDisplayModel.as_view(), name='results'),
    url(r'^results/(?P<model>\w+)/(?P<id>\d+)$', views.ResultsDisplayItem.as_view(), name='results'),
    url(r'^customers.json$', 'SalesEstimates.get_json.customer_json', name='customer_json'),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
