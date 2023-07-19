from django.contrib.auth.middleware import RemoteUserMiddleware


class TequilaRemoteUserMiddleware(RemoteUserMiddleware):
    header = "HTTP_X_CUSTOM_REMOTE_USER"
