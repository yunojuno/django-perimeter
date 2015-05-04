# -*- coding: utf-8 -*-
# perimeter form tests
import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory, override_settings
from django.utils.timezone import now

from perimeter.forms import GatewayForm
from perimeter.models import AccessToken, AccessTokenUse

YESTERDAY = now().date() - datetime.timedelta(days=1)

class GatewayFormTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.payload = {
            'token': "test",
            'email': "hugo@yunojuno.com",
            'name': "Hugo Rodger-Brown"
        }
        self.request = self.factory.post('/',
            data=self.payload,
            REMOTE_ADDR='127.0.0.1',
            HTTP_USER_AGENT='test_agent'
        )
        self.token = AccessToken(token="test").save()
        self.form = GatewayForm(self.request.POST)

    def test_post_valid_token(self):
        self.assertTrue(self.form.is_valid())
        self.assertEqual(self.form.token, self.token)

    def test_clean_inactive_token(self):
        self.token.is_active = False
        self.token.save(update_fields=['is_active'])
        self.assertFalse(self.form.is_valid())
        self.assertRaises(ValidationError, self.form.clean_token)

    def test_clean_expired_token(self):
        self.token.expires_on = YESTERDAY
        self.token.save(update_fields=['expires_on'])
        self.assertFalse(self.form.is_valid())
        self.assertRaises(ValidationError, self.form.clean_token)

    def test_no_matching_token(self):
        AccessToken.objects.all().delete()
        self.assertFalse(self.form.is_valid())
        self.assertRaises(ValidationError, self.form.clean_token)

    def test_save(self):
        self.request.session = {}
        self.assertTrue(self.form.is_valid())
        au = self.form.save(self.request)
        self.assertTrue(AccessTokenUse.objects.get(), au)
        self.assertEqual(au.user_email, self.payload['email'])
        self.assertEqual(au.user_name, self.payload['name'])
        self.assertEqual(au.token, self.token)
        self.assertEqual(au.client_ip, '127.0.0.1')
        self.assertEqual(au.client_user_agent, 'test_agent')
