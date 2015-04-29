# -*- coding: utf-8 -*-
# urls for perimeter app.
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'perimeter.views',
    url(r'^perimeter/$', 'gateway', name='perimeter:gateway'),
)
