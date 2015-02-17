# urls for pubbrain_app
from django.conf.urls import patterns, include, url
from pubbrain_app.views import visualize, index
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import pubbrain_app

urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^visualize/$', 'pubbrain_app.views.visualize', name='visualize')
)
urlpatterns += staticfiles_urlpatterns()