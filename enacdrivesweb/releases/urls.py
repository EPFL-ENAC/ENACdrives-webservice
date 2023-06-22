from django.urls import path, re_path

urlpatterns = [
    path("", "releases.views.http_home"),
    re_path(r"^admin/?$", "releases.views.http_admin", name="http_admin"),
    path("upload", "releases.views.do_upload", name="do_upload"),
    path("enable", "releases.views.do_enable", name="do_enable"),
    path("download", "releases.views.do_download", name="do_download"),
    path(
        "api/latest_release_number",
        "releases.views.api_latest_release_number",
        name="api_latest_release_number",
    ),
    path(
        "api/latest_release_date",
        "releases.views.api_latest_release_date",
        name="api_latest_release_date",
    ),
]
