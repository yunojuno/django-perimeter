import datetime
import random

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .settings import PERIMETER_DEFAULT_EXPIRY


def default_expiry():
    """Return the default expiry date."""
    return (
        timezone.now() +
        datetime.timedelta(days=PERIMETER_DEFAULT_EXPIRY)
    ).date()


class EmptyToken(object):
    """Token-like object that will always return is_valid() == False.

    EmptyToken objects are a bit like Django's AnonymousUser model -
    they return an object that can be used like an AccessToken but that
    is always invalid.
    """
    @property
    def is_valid(self):
        return False


class AccessTokenManager(models.Manager):
    """Custom model manager for AccessTokens."""

    def create_access_token(self, **kwargs):
        """Create a new AccessToken with a random token value."""
        # NB there is a theoretical token clash exception here,
        # when the random_token_value function returns an existing
        # token value, but it is considered so unlikely as to be
        # acceptable.
        kwargs['token'] = kwargs.get('token', AccessToken.random_token_value())
        kwargs['expires_on'] = kwargs.get('expires_on', default_expiry())
        return AccessToken(**kwargs).save()

    def get_access_token(self, token_value):
        """Fetch an AccessToken, return EmptyToken if not found.

        This method is cache-aware, and will check the cache first,
        re-filling it if empty.

        Args:
            token - string, the token value to look up.

        """
        cache_key = AccessToken.get_cache_key(token_value)
        token = cache.get(cache_key)
        if token is None:
            try:
                token = self.get(token=token_value)
                cache.set(token.cache_key, token, token.seconds_to_expiry)
                return token
            except AccessToken.DoesNotExist:
                return EmptyToken()
        else:
            return token


class AccessToken(models.Model):
    """
    A token that allows a user entry to the site via Perimeter.
    """
    token = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    # NB pass in a callable, not the result of the callable, see:
    # http://stackoverflow.com/a/29549675/45698
    expires_on = models.DateField(default=default_expiry)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = AccessTokenManager()

    def __str__(self):
        return self.token

    @classmethod
    def random_token_value(cls):
        """Generate a random token value."""
        return "".join(
            random.sample(
                population=list(
                    "abcdefghijklmnopqrstuvwxyz"
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "1234567890"
                ),
                k=cls._meta.get_field('token').max_length
            )
        )

    @classmethod
    def get_cache_key(cls, token_value):
        return (
            '%s.%s-%s' % (
                cls.__module__,
                cls.__name__,
                token_value
            )
        )

    def save(self, *args, **kwargs):
        "Sets the created_at timestamp."
        self.updated_at = timezone.now()
        self.created_at = self.created_at or self.updated_at
        super(AccessToken, self).save(*args, **kwargs)
        return self

    @property
    def cache_key(self):
        """Return object cache key (from get `get_cache_key`)."""
        return AccessToken.get_cache_key(self.token)

    @property
    def seconds_to_expiry(self):
        """Return the number of seconds till expiry (used for caching)."""
        expires_at = datetime.datetime.combine(self.expires_on, datetime.time.min)
        if settings.USE_TZ and timezone.is_naive(expires_at):
            expires_at = timezone.make_aware(expires_at, timezone.get_current_timezone())
        elif not settings.USE_TZ and timezone.is_aware(expires_at):
            expires_at = timezone.make_naive(expires_at)
        return int((expires_at - timezone.now()).total_seconds())

    @property
    def has_expired(self):
        """Return True if the token has passed expiry date."""
        return self.expires_on < datetime.date.today()

    @property
    def is_valid(self):
        """Return True if the token is active and has not expired."""
        return self.is_active and not self.has_expired

    def record(
        self,
        user_email,
        user_name,
        client_ip='unknown',
        client_user_agent='unknown'
    ):
        """Record the fact that someone has used the token."""
        atu = AccessTokenUse(
            token=self,
            user_email=user_email,
            user_name=user_name,
            client_ip=client_ip,
            client_user_agent=client_user_agent
        )
        atu.save()
        return atu


@receiver(post_save, sender=AccessToken)
def on_save_access_token(sender, instance, **kwargs):
    """Update saved object in cache if is_valid, else delete."""
    cache.set(instance.cache_key, instance, instance.seconds_to_expiry)


@receiver(post_delete, sender=AccessToken)
def on_delete_access_token(sender, instance, **kwargs):
    """Remove deleted object from cache."""
    cache.delete(instance.cache_key)


class AccessTokenUse(models.Model):
    """Audit record used to log whenever an access token is used."""
    token = models.ForeignKey(AccessToken, on_delete=models.CASCADE)
    user_email = models.EmailField(
        verbose_name="Token used by (email)",
        blank=True, null=True
    )
    user_name = models.CharField(
        max_length=100,
        verbose_name="Token used by (name)",
        blank=True, null=True
    )
    client_ip = models.CharField(
        max_length=15,
        verbose_name='IP address',
        blank=True
    )
    client_user_agent = models.TextField(
        verbose_name="Client User Agent",
        blank=True
    )
    timestamp = models.DateTimeField()

    def __str__(self):
        return "'%s' used %s" % (self.token.token, self.timestamp)

    def save(self, *args, **kwargs):
        "Set the timestamp and save the object."
        if 'update_fields' not in kwargs:
            self.timestamp = self.timestamp or timezone.now()
        super(AccessTokenUse, self).save(*args, **kwargs)
        return self
