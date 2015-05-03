# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, RedirectView


urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='homepage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^perimeter/', include('perimeter.urls', namespace='perimeter')),
)
