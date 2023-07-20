from django.urls import path
import config.views

urlpatterns = [
    path(
        "validate_username",
        config.views.http_validate_username,
        name="http_validate_username",
    ),
    path("get", config.views.http_get, name="http_get"),
    path("ldap_settings", config.views.http_ldap_settings, name="http_ldap_settings"),
    path("check", config.views.http_check_config, name="http_check_config"),
]
