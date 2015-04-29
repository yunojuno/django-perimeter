# -*- coding: utf-8 -*-
# perimeter tests
import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory

from perimeter.forms import GatewayForm
from perimeter.models import AccessToken, AccessTokenUse

TODAY = datetime.date.today()
YESTERDAY = TODAY - datetime.timedelta(days=1)
TOMORROW = TODAY + datetime.timedelta(days=1)


class AccessTokenTests(TestCase):

    def test_attrs(self):

        # start with the defaults
        at = AccessToken()
        self.assertEqual(at.token, '')
        self.assertEqual(at.is_active, True)
        self.assertEqual(at.expires_on, TOMORROW)
        self.assertEqual(at.created_at, None)
        self.assertEqual(at.updated_at, None)
        self.assertEqual(at.created_by, None)

        # check the timestamps
        at = at.save()
        self.assertIsNotNone(at.created_at)
        self.assertEqual(at.updated_at, at.created_at)

        # check the timestamps are updated
        x = at.created_at
        at = at.save()
        # created_at is _not_ updated
        self.assertEqual(at.created_at, x)
        # but updated_at _is_
        self.assertTrue(at.updated_at > at.created_at)

    def test_has_expired(self):
        at = AccessToken()
        at.expires_on = YESTERDAY
        self.assertTrue(at.has_expired())
        at.expires_on = TODAY
        self.assertFalse(at.has_expired())
        at.expires_on = TOMORROW
        self.assertFalse(at.has_expired())

    def test_is_valid(self):

        def assertValidity(active, expires, valid):
            return AccessToken(is_active=True, expires_on=TOMORROW).is_valid()

        assertValidity(True, YESTERDAY, False)
        assertValidity(True, TODAY, True)
        assertValidity(True, TOMORROW, True)

        assertValidity(False, YESTERDAY, False)
        assertValidity(False, TODAY, False)
        assertValidity(False, TOMORROW, False)

    def test_record(self):
        at = AccessToken(token="test_token").save()
        atu = at.record("hugo@yunojuno.com", "Hugo")
        self.assertEqual(atu, AccessTokenUse.objects.get())
        self.assertEqual(atu.email, "hugo@yunojuno.com")
        self.assertEqual(atu.name, "Hugo")
        self.assertIsNotNone(atu.timestamp, "Hugo")
        self.assertEqual(atu.client_ip, "unknown")
        self.assertEqual(atu.client_user_agent, "unknown")

class AccesTokenUseTests(TestCase):
    pass


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
        self.assertTrue(self.form.is_valid())
        au = self.form.save(self.request)
        self.assertTrue(AccessTokenUse.objects.get(), au)
        self.assertEqual(au.email, self.payload['email'])
        self.assertEqual(au.name, self.payload['name'])
        self.assertEqual(au.token, self.token)
        self.assertEqual(au.client_ip, '127.0.0.1')
        self.assertEqual(au.client_user_agent, 'test_agent')


class PerimeterMiddlewareTests(TestCase):

    def test_missing_user(self):
        self.fail("Write me")

    def test_missing_session(self):
        self.fail("Write me")

    def test_authenticated_user(self):
        self.fail("Write me")

    def test_admin_paths(self):
        self.fail("Write me")

    def test_missing_token(self):
        self.fail("Write me")

    def test_invalid_token(self):
        self.fail("Write me")
