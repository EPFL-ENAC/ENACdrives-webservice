from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path("", "releases.views.http_home"),
    path("admin/", include(admin.site.urls)),
    path("config/", include("config.urls")),
    path("releases/", include("releases.urls")),
]
