# urls for pubbrain_app
from django.conf.urls import patterns, include, url
from pubbrain_app.views import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import pubbrain_app


urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^json', tree_json_view, name='json'),
    url(r'^(?P<pk>\d+)/papaya/embedview$', 
        papaya_js_embed,
        {'iframe':True},name='papaya_iframe_embed'),
    url(r'^pubsearch', search, name='pubbrain_search'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<pk>\d+)/js/embed$',
        papaya_js_embed,
        name='papaya_js_embed'),
    url(r'^datatable/results$', OrderListJson.as_view(), name='order_list_json'),
    url(r'^search/', include('haystack.urls')),
)
        
urlpatterns += staticfiles_urlpatterns()