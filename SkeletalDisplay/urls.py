from django.conf.urls import patterns, include, url

urlpatterns = patterns('SkeletalDisplay.views',
    url(r'^$', 'index', name='index'),
    url(r'^X/(\w+)/(\w+)/(\d+)$', 'display_item', name='display_item'),
    url(r'^X/(\w+)/(\w+)$', 'display_model', name='display_model'),
)