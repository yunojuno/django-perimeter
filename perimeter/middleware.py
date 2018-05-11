"""
Middleware component of Perimeter app - checks all incoming requests for a
valid token. See Perimeter docs for more details.
"""
from urllib.parse import urlencode

from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from .models import AccessToken
from .settings import (
    PERIMETER_SESSION_KEY,
    PERIMETER_ENABLED,
    PERIMETER_BYPASS_FUNCTION as bypass_perimeter
)


def get_request_token(request):
    """Returns AccessToken if found else EmptyToken."""
    assert hasattr(request, 'session'), (
        "Missing session attribute - please check MIDDLEWARE_CLASSES for "
        "'django.contrib.sessions.middleware.SessionMiddleware'."
    )
    token_value = request.session.get(PERIMETER_SESSION_KEY, None)
    # NB this method implements caching, so is more performant
    # than the straight get() alternative
    return AccessToken.objects.get_access_token(token_value)


def set_request_token(request, token_value):
    """Sets the request.session token value.

    Args:
        token - string, the token value (not the token object, as that is
            not serializable)
    """
    assert hasattr(request, 'session'), (
        "Missing session attribute - please check MIDDLEWARE_CLASSES for "
        "'django.contrib.sessions.middleware.SessionMiddleware'."
    )
    request.session[PERIMETER_SESSION_KEY] = token_value


class PerimeterAccessMiddleware(MiddlewareMixin):
    """
    Middleware used to detect whether user can access site or not.

    This middleware will be disabled if the PERIMETER_ENABLED setting does not
    exist in django settings, or is False.
    """
    def __init__(self, *args, **kwargs):
        """
        Disable middleware if PERIMETER_ENABLED setting not True.

        Raises MiddlewareNotUsed exception if the PERIMETER_ENABLED setting
        is not True - this is used by Django framework to remove the middleware.
        """
        if PERIMETER_ENABLED is False:
            raise MiddlewareNotUsed()
        super(PerimeterAccessMiddleware, self).__init__(*args, **kwargs)

    def process_request(self, request):
        """Check user session for token."""
        if bypass_perimeter(request):
            return None

        if get_request_token(request).is_valid:
            return None

        # redirect to the gateway for validation,
        qstring = urlencode({'next': request.get_full_path()})
        return HttpResponseRedirect(
            reverse('perimeter:gateway') + '?' + qstring
        )
