from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

import perimeter.urls

admin.autodiscover()

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="homepage"),
    path("admin/", admin.site.urls),
    path("perimeter/", include(perimeter.urls)),
]
