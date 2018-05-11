from urllib.parse import urlparse

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse, resolve

from ..middleware import (
    PerimeterAccessMiddleware,
    bypass_perimeter,
    get_request_token,
    PERIMETER_SESSION_KEY
)
from ..models import (
    AccessToken,
    EmptyToken
)


@override_settings(PERIMETER_ENABLED=True)
class PerimeterMiddlewareTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        # spoof the Auth and Session middleware
        self.request.user = User()
        self.request.session = {}
        self.middleware = PerimeterAccessMiddleware()

    def _assertRedirectsToGateway(self, request, query=None):
        query = query or "next=%2F"
        # NB assertRedirects doesn't work!
        resp = self.middleware.process_request(request)
        self.assertEqual(resp.status_code, 302)
        # use a resolver to strip off any quesrystring params
        resolver = resolve(resp.url)
        self.assertEqual(resolver.url_name, 'gateway')
        self.assertEqual(resolver.namespace, 'perimeter')
        self.assertEqual(urlparse(resp.url).query, query)

    def test_bypass_perimeter_default(self):
        """Perimeter login urls excluded."""
        request = self.factory.get('/')
        self.assertFalse(bypass_perimeter(request))
        request = self.factory.get(reverse('perimeter:gateway'))
        self.assertTrue(bypass_perimeter(request))

    def test_get_request_token(self):
        at = AccessToken.objects.create_access_token()
        self.request.session[PERIMETER_SESSION_KEY] = at.token
        self.assertEqual(get_request_token(self.request), at)

    def test_get_request_token_empty(self):
        token = get_request_token(self.request)
        self.assertTrue(type(token) == EmptyToken)

    def test_missing_session(self):
        """Missing request.session should raise AssertionError."""
        del self.request.session
        self.assertRaises(
            AssertionError,
            get_request_token,
            self.request
        )

    def test_missing_token(self):
        """AnonymousUser without a token should be denied."""
        self.request.user = AnonymousUser()
        self._assertRedirectsToGateway(self.request)

    def test_invalid_token(self):
        self.request.user = AnonymousUser()
        self.request.session['token'] = "foobar"
        self._assertRedirectsToGateway(self.request)

    def test_valid_token(self):
        """AnonymousUser with a valid session token should pass through."""
        AccessToken(token="foobar").save()
        self.request.user = AnonymousUser()
        self.request.session['token'] = "foobar"
        self._assertRedirectsToGateway(self.request)

    def test_next_query_string_set(self):
        """Check `next` query string param is properly encoded"""

        # Simple path
        request = self.factory.get('/somepath/')
        request.user = AnonymousUser()
        request.session = {}
        self._assertRedirectsToGateway(
            request, query="next=%2Fsomepath%2F"
        )

        # Path with query string
        request = self.factory.get('/somepath/?important=param')
        request.user = AnonymousUser()
        request.session = {}
        self._assertRedirectsToGateway(
            request,
            query="next=%2Fsomepath%2F%3Fimportant%3Dparam"
        )
