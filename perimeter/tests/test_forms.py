import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from django.utils.timezone import now

from ..forms import TokenGatewayForm, UserGatewayForm
from ..models import AccessToken, AccessTokenUse

YESTERDAY = now().date() - datetime.timedelta(days=1)


class BaseGatewayFormTests(TestCase):

    def get_request(self, payload):
        request = self.factory.post(
            '/',
            data=payload,
            REMOTE_ADDR='127.0.0.1',
            HTTP_USER_AGENT='test_agent'
        )
        request.session = {}
        return request

    def get_form(self, klass, payload):
        request = self.get_request(payload)
        form = klass(request.POST)
        return form

    def setUp(self):
        self.factory = RequestFactory()
        self.payload = {
            'token': "test",
        }
        self.token = AccessToken(token="test").save()


class TokenGatewayFormTests(BaseGatewayFormTests):

    def test_post_valid_token(self):
        form = self.get_form(TokenGatewayForm, self.payload)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.token, self.token)
        # test with user info missing
        payload = {'token': self.payload['token']}
        form = self.get_form(TokenGatewayForm, payload)
        self.assertTrue(form.is_valid())

    def test_clean_inactive_token(self):
        form = self.get_form(TokenGatewayForm, self.payload)
        self.token.is_active = False
        self.token.save(update_fields=['is_active'])
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError, form.clean_token)

    def test_clean_expired_token(self):
        form = self.get_form(TokenGatewayForm, self.payload)
        self.token.expires_on = YESTERDAY
        self.token.save(update_fields=['expires_on'])
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError, form.clean_token)

    def test_no_matching_token(self):
        form = self.get_form(TokenGatewayForm, self.payload)
        AccessToken.objects.all().delete()
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError, form.clean_token)

    def test_save(self):
        request = self.get_request(self.payload)
        form = self.get_form(TokenGatewayForm, self.payload)
        self.assertTrue(form.is_valid())
        au = form.save(request)
        self.assertTrue(AccessTokenUse.objects.get(), au)
        self.assertIsNone(au.user_email)
        self.assertIsNone(au.user_name)
        self.assertEqual(au.token, self.token)
        self.assertEqual(au.client_ip, '127.0.0.1')
        self.assertEqual(au.client_user_agent, 'test_agent')


class UserGatewayFormTests(BaseGatewayFormTests):

    def setUp(self):
        super(UserGatewayFormTests, self).setUp()

    def test_clean_email(self):
        form = self.get_form(UserGatewayForm, self.payload)
        self.assertFalse(form.is_valid())
        self.payload['email'] = 'fred@example.com'
        self.payload['name'] = 'Fred'
        form = self.get_form(UserGatewayForm, self.payload)
        self.assertTrue(form.is_valid())

    def test_save(self):
        request = self.get_request(self.payload)
        form = self.get_form(TokenGatewayForm, self.payload)
        self.assertTrue(form.is_valid())
        au = form.save(request)
        self.assertTrue(AccessTokenUse.objects.get(), au)
        self.assertIsNone(au.user_email)
        self.assertIsNone(au.user_name)
        self.assertEqual(au.token, self.token)
        self.assertEqual(au.client_ip, '127.0.0.1')
        self.assertEqual(au.client_user_agent, 'test_agent')
