from django.contrib import admin
try:
    from django.urls import re_path, include
except ImportError:
    from django.conf.urls import url as re_path, include
from django.views.generic import TemplateView

import perimeter.urls

admin.autodiscover()

urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='index.html'), name='homepage'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^perimeter/', include(perimeter.urls)),
]
