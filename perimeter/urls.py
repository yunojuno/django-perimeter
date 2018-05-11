try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from . import views

app_name = 'perimeter'

urlpatterns = [
    re_path(r'^gateway/', views.gateway, name='gateway'),
]
