from django.conf.urls import patterns, include, url

urlpatterns = patterns('SkeletalDisplay.views',
    url(r'^$', 'index', name='index'),
    url(r'^X/(\w+)/(\w+)/(\d+)$', 'display_item', name='display_item'),
    url(r'^X/(\w+)/(\w+)$', 'display_model', name='display_model'),
)

urlpatterns += patterns('SkeletalDisplay.editor',
    url(r'^add/(\w+)/(\w+)$', 'add_item', name='add_item'),
    url(r'^edit/(\w+)/(\w+)/(\d+)$', 'edit_item', name='edit_item'),
    url(r'^delete/(\w+)/(\w+)/(\d+)$', 'delete_item', name='delete_item'),
)