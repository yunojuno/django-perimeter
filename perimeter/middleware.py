"""
Check all incoming requests for a valid token.

See Perimeter docs for more details.

"""

from typing import Any, Callable, Optional, Union
from urllib.parse import urlencode

from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from .models import AccessToken, EmptyToken
from .settings import (
    HTTP_X_PERIMETER_TOKEN,
    PERIMETER_BYPASS_FUNCTION as bypass_perimeter,
    PERIMETER_ENABLED,
    PERIMETER_SESSION_KEY,
)


def check_middleware(func: Callable) -> Callable:
    """Check a request arg has a Session attached."""

    def inner(request: HttpRequest, *args: Any) -> Optional[HttpResponse]:
        if not hasattr(request, "session"):
            raise ImproperlyConfigured(
                "Missing session attribute - please check MIDDLEWARE_CLASSES for "
                "'django.contrib.sessions.middleware.SessionMiddleware'."
            )
        return func(request, *args)

    return inner


@check_middleware
def get_request_token(request: HttpRequest) -> Optional[str]:
    """Extract token string from HTTP header or querystring."""
    return request.META.get(HTTP_X_PERIMETER_TOKEN, None) or request.session.get(
        PERIMETER_SESSION_KEY, None
    )


@check_middleware
def set_request_token(request: HttpRequest, token_value: str) -> None:
    """Set the request.session token value."""
    request.session[PERIMETER_SESSION_KEY] = token_value


def get_access_token(request: HttpRequest) -> Union[AccessToken, EmptyToken]:
    """Fetch the AccessToken from the request."""
    token_value = get_request_token(request)
    return AccessToken.objects.get_access_token(token_value)


def get_redirect_url(request: HttpRequest) -> str:
    """Unpack request and extract a valid redirect url."""
    qstring = urlencode({"next": request.get_full_path()})
    url = reverse("perimeter:gateway")
    return f"{url}?{qstring}"


class PerimeterAccessMiddleware(MiddlewareMixin):
    """
    Middleware used to detect whether user can access site or not.

    This middleware will be disabled if the PERIMETER_ENABLED setting does not
    exist in django settings, or is False.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Disable middleware if PERIMETER_ENABLED setting not True.

        Raises MiddlewareNotUsed exception if the PERIMETER_ENABLED setting
        is not True - this is used by Django framework to remove the middleware.
        """
        if PERIMETER_ENABLED is False:
            raise MiddlewareNotUsed("Perimeter disabled")
        super().__init__(*args, **kwargs)

    def process_request(self, request: HttpRequest) -> Optional[HttpResponseRedirect]:
        """Check user session for token."""
        if bypass_perimeter(request):
            return None

        if get_access_token(request).is_valid:
            return None

        return HttpResponseRedirect(get_redirect_url(request))
