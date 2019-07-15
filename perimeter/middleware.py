"""
Middleware component of Perimeter app - checks all incoming requests for a
valid token. See Perimeter docs for more details.
"""
from urllib.parse import urlencode

from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from .models import AccessToken
from .settings import PERIMETER_BYPASS_FUNCTION as bypass_perimeter
from .settings import PERIMETER_ENABLED
from .settings import HTTP_X_PERIMETER_TOKEN, PERIMETER_SESSION_KEY


def get_request_token(request):
    """Extract token string from HTTP header or querystring."""
    return request.META.get(HTTP_X_PERIMETER_TOKEN, None) or request.session.get(
        PERIMETER_SESSION_KEY, None
    )


def set_request_token(request, token_value):
    """Sets the request.session token value.

    Args:
        token - string, the token value (not the token object, as that is
            not serializable)
    """
    request.session[PERIMETER_SESSION_KEY] = token_value


def check_middleware(request):
    """Check that Session middleware is installed."""
    if not hasattr(request, "session"):
        raise ImproperlyConfigured(
            "Missing session attribute - please check MIDDLEWARE_CLASSES for "
            "'django.contrib.sessions.middleware.SessionMiddleware'."
        )


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
            raise MiddlewareNotUsed("Perimeter disabled")
        super().__init__(*args, **kwargs)

    def access_token(self, request):
        """Fetch the AccessToken from the request."""
        token_value = get_request_token(request)
        return AccessToken.objects.get_access_token(token_value)

    def process_request(self, request):
        """Check user session for token."""
        check_middleware(request)

        if bypass_perimeter(request):
            return None

        if self.access_token(request).is_valid:
            return None

        # redirect to the gateway for validation,
        qstring = urlencode({"next": request.get_full_path()})
        url = reverse("perimeter:gateway")
        return HttpResponseRedirect(f"{url}?{qstring}")
