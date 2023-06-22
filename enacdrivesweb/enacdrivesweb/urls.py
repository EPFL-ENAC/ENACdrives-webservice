from django.urls import include, path
from django.contrib import admin
import releases.views

urlpatterns = [
    path("", releases.views.http_home),
    path("admin/", admin.site.urls),
    path("config/", include("config.urls")),
    path("releases/", include("releases.urls")),
]
