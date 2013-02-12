"""
Middleware component of Perimeter app - checks all incoming requests for a
valid token. See Perimeter docs for more details.
"""
import logging

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed, PermissionDenied
from django.http import HttpResponseForbidden

from .models import AccessToken

logger = logging.getLogger(__name__)


class PerimeterAccessMiddleware(object):
    """
    Middleware used to detect whether user can access site or not.

    This middleware will be disabled if the PERIMETER_ENABLED setting does not
    exist in django settings, or is False.
    """
    def __init__(self):
        """
        Disable middleware if PERIMETER_ENABLED setting not True.

        Raises MiddlewareNotUsed exception if the PERIMETER_ENABLED setting
        is not True - this is used by Django framework to remove the middleware.
        """
        try:
            enabled = settings.PERIMETER_ENABLED
            if not bool(enabled):
                logger.info("Perimeter is down. PERIMETER_ENABLED is False.")
                raise MiddlewareNotUsed()
        except AttributeError:
            logger.info("Perimeter is down. PERIMETER_ENABLED missing.")
            raise MiddlewareNotUsed()

        try:
            self.PERIMETER_SESSION_KEY = settings.PERIMETER_SESSION_KEY
        except AttributeError:
            self.PERIMETER_SESSION_KEY = 'pt'

    def process_request(self, request):
        """
        Check incoming request for access token (in session & querystring).
        """
        # if you can't access the admin site you can't create a token - this
        # wouldn't really work.
        # TODO: hook up dynamically to admin URLs
        if request.path[:6] == '/admin':
            return None

        token = request.session.get(self.PERIMETER_SESSION_KEY, False)
        if token:
            if token.is_valid():
                return None
            else:
                # it's invalid, so blat it.
                del request.session[self.PERIMETER_SESSION_KEY]

        # we don't have a good token, so check querystring
        token_id = request.GET.get(self.PERIMETER_SESSION_KEY, False)
        if token_id:
            try:
                token = AccessToken.objects.get(token=token_id)
                if token.is_valid():
                    ip = request.META.get('HTTP_X_FORWARDED_FOR', 'unknown')
                    ua = request.META.get('HTTP_USER_AGENT', 'unknown')
                    token.record_usage(client_ip=ip, client_user_agent=ua)
                    request.session[self.PERIMETER_SESSION_KEY] = token
                else:
                    return PermissionDenied()
            except AccessToken.DoesNotExist:
                return PermissionDenied()
        else:
            raise PermissionDenied()
