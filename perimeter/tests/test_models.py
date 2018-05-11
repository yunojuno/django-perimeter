from datetime import datetime, date, time, timedelta

from django.core.cache import cache
from django.test import TestCase
from django.utils.timezone import (
    now,
    is_aware,
    is_naive,
    make_aware,
    get_current_timezone
)

from ..models import (
    AccessToken,
    AccessTokenUse,
    default_expiry,
    EmptyToken
)
from ..settings import PERIMETER_DEFAULT_EXPIRY

TODAY = now().date()
YESTERDAY = TODAY - timedelta(days=1)
TOMORROW = TODAY + timedelta(days=1)


class EmptyTokenTests(TestCase):

    def test_is_valid(self):
        """EmptyToken should always be invalid."""
        token = EmptyToken()
        self.assertFalse(token.is_valid)


class AccessTokenManagerTests(TestCase):

    def test_create_with_token(self):
        """If a token is passed in to create_access_token, it's used."""
        token = AccessToken.objects.create_access_token(token='x')
        self.assertEqual(token, AccessToken.objects.get())
        self.assertTrue(token, 'x')

    def test_create_with_expires(self):
        """If an expires is passed in to create_access_token, it's used."""
        tomorrow = date.today() + timedelta(days=1)
        token = AccessToken.objects.create_access_token(expires_on=tomorrow)
        self.assertEqual(token, AccessToken.objects.get())
        self.assertTrue(token.expires_on, tomorrow)

    def test_create_without_token(self):
        """If no token is passed in to create_access_token, a random one is used."""
        token = AccessToken.objects.create_access_token()
        self.assertEqual(token, AccessToken.objects.get())
        self.assertTrue(len(token.token), 10)

    def test_get_access_token(self):
        """Test the caching works."""
        token = AccessToken.objects.create_access_token()
        cache.clear()
        self.assertIsNone(cache.get(token.cache_key))
        token2 = AccessToken.objects.get_access_token(token.token)
        self.assertEqual(token, token2)
        self.assertIsNotNone(cache.get(token.cache_key))


class AccessTokenTests(TestCase):

    def test_default_expiry(self):
        self.assertEqual(
            default_expiry(),
            now().date() + timedelta(days=PERIMETER_DEFAULT_EXPIRY)
        )

    def test_attrs(self):
        # start with the defaults
        at = AccessToken()
        self.assertEqual(at.token, '')
        self.assertEqual(at.is_active, True)
        self.assertEqual(at.expires_on, default_expiry())
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

        self.assertTrue(at.is_valid)
        self.assertFalse(at.has_expired)

    def test_str(self):
        today = date.today()
        at = AccessToken(token="¡€#¢∞§¶•ªº", expires_on=today, is_active=True)
        self.assertEqual(str(at), '¡€#¢∞§¶•ªº')

    def test_cache_key(self):
        token = AccessToken(token="test")
        self.assertIsNotNone(token.cache_key)
        self.assertEqual(token.cache_key, AccessToken.get_cache_key("test"))

    def test_cache_management(self):
        token = AccessToken.objects.create_access_token()
        self.assertEqual(cache.get(token.cache_key), token)
        token.delete()
        self.assertIsNone(cache.get(token.cache_key))

    def test_generate_random_token(self):
        f = AccessToken._meta.get_field('token').max_length
        t1 = AccessToken.random_token_value()
        t2 = AccessToken.random_token_value()
        self.assertNotEqual(t1, t2)
        self.assertEqual(len(t1), f)

    def test_has_expired(self):
        at = AccessToken()
        at.expires_on = YESTERDAY
        self.assertTrue(at.has_expired)
        at.expires_on = TODAY
        self.assertFalse(at.has_expired)
        at.expires_on = TOMORROW
        self.assertFalse(at.has_expired)

    def test_seconds_to_expiry(self):
        "Test that it handles naive and tz-aware times"

        with self.settings(USE_TZ=False):
            at = AccessToken(expires_on=TOMORROW)
            expires_at = datetime.combine(at.expires_on, time.min)
            self.assertTrue(is_naive(expires_at))
            self.assertTrue(is_naive(now()))
            self.assertEqual(
                at.seconds_to_expiry,
                int((expires_at - now()).total_seconds())
            )

        with self.settings(USE_TZ=True):
            at = AccessToken(expires_on=TOMORROW)
            expires_at = make_aware(
                datetime.combine(at.expires_on, time.min),
                get_current_timezone()
            )
            self.assertTrue(is_aware(expires_at))
            self.assertTrue(is_aware(now()))
            self.assertEqual(
                at.seconds_to_expiry,
                int((expires_at - now()).total_seconds())
            )

    def test_is_valid(self):

        def assertValidity(active, expires, valid):
            return AccessToken(is_active=True, expires_on=TOMORROW).is_valid

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
        self.assertEqual(atu.user_email, "hugo@yunojuno.com")
        self.assertEqual(atu.user_name, "Hugo")
        self.assertIsNotNone(atu.timestamp, "Hugo")
        self.assertEqual(atu.client_ip, "unknown")
        self.assertEqual(atu.client_user_agent, "unknown")


class AccesTokenUseTests(TestCase):

    def setUp(self):
        self.token = AccessToken(token='foo').save()

    def test_save(self):
        atu = AccessTokenUse(token=self.token)
        atu.save()
        self.assertIsNone(atu.user_email)
        self.assertIsNone(atu.user_name)
