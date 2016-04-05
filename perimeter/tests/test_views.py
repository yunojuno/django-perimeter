# -*- coding: utf-8 -*-
# perimeter view tests
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory, override_settings

from perimeter.models import AccessToken, AccessTokenUse
from perimeter.views import resolve_return_url, gateway


class PerimeterViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('perimeter:gateway')

    def test_display_gateway_GET_200(self):
        """GET on the perimeter:gateway should work."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'perimeter/gateway.html')

    def test_display_gateway_POST_302(self):
        """POST on the perimeter:gateway should work."""
        token = AccessToken.objects.create_access_token()
        payload = {
            'token': token.token,
            'email': 'hugo@example.com',
            'name': 'Hugo Rodger-Brown',
        }
        request = self.factory.post(self.url, payload)
        request.session = {}
        response = gateway(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], self.url)
        usage = AccessTokenUse.objects.get()
        self.assertEqual(usage.user_email, payload['email'])
        self.assertEqual(usage.user_name, payload['name'])
        self.assertEqual(usage.token, token)

        # Check the next url is decoded and used properly
        url = self.url + "?next=%2Fadmin%2F%3Fimportant%3Dparam"
        request = self.factory.post(url, payload)
        request.session = {}
        response = gateway(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "/admin/?important=param")

    def test_resolve_return_url(self):
        default_url = reverse('perimeter:gateway')
        for url in (None, 'x/y/z/', default_url):
            self.assertEqual(resolve_return_url(url), default_url)
