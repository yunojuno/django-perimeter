# -*- coding: utf-8 -*-
# urls for perimeter app.
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'perimeter.views',
    url(r'^gateway/', 'gateway', name='gateway'),
)
