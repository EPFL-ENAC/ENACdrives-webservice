from django.contrib.auth.middleware import RemoteUserMiddleware
from django.utils.deprecation import MiddlewareMixin

class TequilaRemoteUserMiddleware(RemoteUserMiddleware):
    header = "HTTP_X_CUSTOM_REMOTE_USER"

class FixForwardedHostMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'HTTP_X_FORWARDED_HOST' in request.META:
            request.META['HTTP_X_FORWARDED_HOST'] = request.META['HTTP_X_FORWARDED_HOST'].split(',')[0].strip()
