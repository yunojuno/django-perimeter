# -*- coding: utf-8 -*-
"""
Middleware component of Perimeter app - checks all incoming requests for a
valid token. See Perimeter docs for more details.
"""
import logging

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed, PermissionDenied

from perimeter.models import AccessToken

logger = logging.getLogger(__name__)

PERIMETER_SESSION_KEY = getattr(settings, 'PERIMETER_SESSION_KEY', 'perimeter')


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
        if not getattr(settings, 'PERIMETER_ENABLED', False):
            raise MiddlewareNotUsed()

    def process_request(self, request):
        """Check user session for token."""
        assert hasattr(request, 'user'), (
            "Missing user attribute - please check MIDDLEWARE_CLASSES for "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        assert hasattr(request, 'session'), (
            "Missing session attribute - please check MIDDLEWARE_CLASSES for "
            "'django.contrib.sessions.middleware.SessionMiddleware'."
        )
        # if the user is authenticated, then let them in regardlesss
        if request.user.is_authenticated():
            return None

        # if you can't access the admin site you can't create a token - this
        # wouldn't really work.
        # TODO: hook up dynamically to admin URLs
        if request.path[:6] == '/admin':
            return None

        token = request.session.get(PERIMETER_SESSION_KEY)
        if token is None:
            raise PermissionDenied()

        if not token.is_valid():
            # it's invalid, so remove it.
            del request.session[PERIMETER_SESSION_KEY]
            raise PermissionDenied()

        # we have a token, and it's valid
        return None
