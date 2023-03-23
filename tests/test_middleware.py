from unittest import mock
from urllib.parse import urlparse

from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.test import RequestFactory, TestCase, override_settings
from django.urls import resolve, reverse

from perimeter.middleware import (
    PERIMETER_SESSION_KEY,
    PerimeterAccessMiddleware,
    bypass_perimeter,
    check_middleware,
    get_access_token,
    get_request_token,
    set_request_token,
)
from perimeter.models import AccessToken, EmptyToken


@override_settings(PERIMETER_ENABLED=True)
class PerimeterMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        # spoof the Auth and Session middleware
        self.request.user = User()
        self.request.session = {}
        get_response = mock.MagicMock
        self.middleware = PerimeterAccessMiddleware(get_response=get_response)

    def _assertRedirectsToGateway(self, request, query=None):
        query = query or "next=%2F"
        # NB assertRedirects doesn't work!
        resp = self.middleware(request)
        self.assertEqual(resp.status_code, 302)
        # use a resolver to strip off any querystring params
        resolver = resolve(resp.url)
        self.assertEqual(resolver.url_name, "gateway")
        self.assertEqual(resolver.namespace, "perimeter")
        self.assertEqual(urlparse(resp.url).query, query)

    def test_middleware_disabled(self):
        with mock.patch("perimeter.middleware.PERIMETER_ENABLED", False):
            self.assertRaises(MiddlewareNotUsed, PerimeterAccessMiddleware)

    def test_bypass_perimeter_default(self):
        """Perimeter login urls excluded."""
        request = self.factory.get("/")
        self.assertFalse(bypass_perimeter(request))
        request = self.factory.get(reverse("perimeter:gateway"))
        self.assertTrue(bypass_perimeter(request))

    def test_get_request_token_session(self):
        at = AccessToken.objects.create_access_token()
        self.request.session[PERIMETER_SESSION_KEY] = at.token
        self.assertEqual(get_request_token(self.request), at.token)

    def test_get_request_token_http_header(self):
        at = AccessToken.objects.create_access_token()
        request = self.factory.get("/", HTTP_X_PERIMETER_TOKEN=at.token)
        request.session = {}
        self.assertEqual(get_request_token(request), at.token)

    def test_get_request_token_empty(self):
        token = get_request_token(self.request)
        self.assertIsNone(token)

    def test_set_request_token(self):
        self.assertIsNone(get_request_token(self.request))
        set_request_token(self.request, "foo")
        self.assertEqual(get_request_token(self.request), "foo")

    def test_get_access_token(self):
        at = AccessToken.objects.create_access_token()
        self.request.session[PERIMETER_SESSION_KEY] = at.token
        self.assertEqual(get_access_token(self.request), at)

    def test_access_token_empty(self):
        token = get_access_token(self.request)
        self.assertIsInstance(token, EmptyToken)

    def test_check_middleware(self):
        """Missing request.session should raise AssertionError."""
        self.assertEqual(check_middleware(lambda r: r)(self.request), self.request)

    def test_check_middleware_fails(self):
        """Missing request.session should raise AssertionError."""
        self.assertEqual(check_middleware(lambda r: r)(self.request), self.request)
        del self.request.session
        with self.assertRaises(ImproperlyConfigured):
            check_middleware(lambda r: r)(self.request)

    def test_missing_session(self):
        """Missing request.session should raise AssertionError."""
        del self.request.session
        self.assertRaises(ImproperlyConfigured, self.middleware, self.request)

    def test_missing_token(self):
        """An AnonymousUser without a token should be denied."""
        self.request.user = AnonymousUser()
        self._assertRedirectsToGateway(self.request)

    def test_invalid_token(self):
        self.request.user = AnonymousUser()
        self.request.session["token"] = "foobar"
        self._assertRedirectsToGateway(self.request)

    def test_valid_token(self):
        """An AnonymousUser with a valid session token should pass through."""
        AccessToken(token="foobar").save()
        self.request.user = AnonymousUser()
        self.request.session["token"] = "foobar"
        self._assertRedirectsToGateway(self.request)

    def test_perimeter_token_header(self):
        """Test that the X-Perimeter-Token header works."""
        AccessToken(token="foobar").save()
        self.request.user = AnonymousUser()
        self._assertRedirectsToGateway(self.request)
        self.request.META["HTTP_X_PERIMETER_TOKEN"] = "foobar"
        self.middleware(self.request)

    def test_next_query_string_set(self):
        """Check `next` query string param is properly encoded."""
        # Simple path
        request = self.factory.get("/somepath/")
        request.user = AnonymousUser()
        request.session = {}
        self._assertRedirectsToGateway(request, query="next=%2Fsomepath%2F")

        # Path with query string
        request = self.factory.get("/somepath/?important=param")
        request.user = AnonymousUser()
        request.session = {}
        self._assertRedirectsToGateway(
            request, query="next=%2Fsomepath%2F%3Fimportant%3Dparam"
        )
