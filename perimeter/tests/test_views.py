# -*- coding: utf-8 -*-
# perimeter view tests
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from perimeter.models import AccessToken, AccessTokenUse


@override_settings(PERIMETER_ENABLED=True)
class PerimeterViewTests(TestCase):

    def test_display_gateway_GET_200(self):
        """GET on the perimeter:gateway should work."""
        response = self.client.get(reverse('perimeter:gateway'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gateway.html')

    def test_display_gateway_POST_302(self):
        """POST on the perimeter:gateway should work."""
        token = AccessToken.objects.create_access_token()
        payload = {
            'token': token.token,
            'email': 'hugo@example.com',
            'name': 'Hugo Rodger-Brown',
        }
        response = self.client.post(
            reverse('perimeter:gateway'),
            payload
        )
        self.assertEqual(response.status_code, 302)
        usage = AccessTokenUse.objects.get()
        self.assertEqual(usage.email, payload['email'])
        self.assertEqual(usage.name, payload['name'])
        self.assertEqual(usage.token, token)
