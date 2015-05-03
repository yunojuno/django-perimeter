# -*- coding: utf-8 -*-
"""
Django models for the Perimeter app.
"""
from datetime import date, timedelta
import random

from django.conf import settings
from django.contrib.admin import site, ModelAdmin
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


def default_expiry():
    """Return the default expiry date."""
    days = getattr(settings, 'PERIMETER_DEFAULT_EXPIRY', 7)
    return (now() + timedelta(days=days)).date()


class EmptyToken(object):
    """Token-like object that will always return is_valid() == False.

    EmptyToken objects are a bit like Django's AnonymousUser model -
    they return an object that can be used like an AccessToken but that
    is always invalid.
    """
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
        return AccessToken(**kwargs).save()

    def get_access_token(self, token):
        """Fetch an AccessToken, return EmptyToken if not found.

        Args:
            token - string, the token value to look up.

        """
        try:
            return self.get(token=token)
        except AccessToken.DoesNotExist:
            return EmptyToken()


class AccessToken(models.Model):
    """
    A token that allows a user entry to the site via Perimeter.
    """
    token = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    # NB pass in a callable, not the result of the callable, see:
    # http://stackoverflow.com/a/29549675/45698
    expires_on = models.DateField(default=default_expiry)
    created_by = models.ForeignKey(User, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = AccessTokenManager()

    def __unicode__(self):
        return u"Access token: %s" % self.token

    def __str__(self):
        return self.__unicode__().encode('UTF-8')

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

    def save(self, *args, **kwargs):
        "Sets the created_at timestamp."
        self.updated_at = now()
        self.created_at = self.created_at or self.updated_at
        super(AccessToken, self).save(*args, **kwargs)
        return self

    def has_expired(self):
        """Return True if the token has passed expiry date."""
        return self.expires_on < date.today()

    def is_valid(self):
        """Return True if the token is active and has not expired."""
        return self.is_active and not self.has_expired()

    def record(self, email, user_name,
        client_ip='unknown', client_user_agent='unknown'):
        """Record the fact that someone has used the token."""
        atu = AccessTokenUse(
            token=self,
            email=email,
            name=user_name,
            client_ip=client_ip,
            client_user_agent=client_user_agent
        )
        atu.save()
        return atu


class AccessTokenAdmin(ModelAdmin):

    raw_id_fields = ('created_by',)
    list_display = ('token', 'expires_on', 'is_active', 'created_at', 'created_by')


class AccessTokenUse(models.Model):
    """Audit record used to log whenever an access token is used."""
    token = models.ForeignKey(AccessToken)
    email = models.EmailField(
        verbose_name="User's email")
    name = models.CharField(max_length=100,
        verbose_name="User's name")
    client_ip = models.CharField(
        max_length=15,
        verbose_name='IP address',
        blank=True
    )
    client_user_agent = models.CharField(
        max_length=150,
        verbose_name="User Agent",
        blank=True
    )
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return u"Token '%s' used at %s" % (self.token.token, self.timestamp)

    def __str__(self):
        return self.__unicode__().encode('UTF-8')

    def save(self, *args, **kwargs):
        "Set the timestamp and save the object."
        self.timestamp = self.timestamp or now()
        super(AccessTokenUse, self).save(*args, **kwargs)
        return self


class AccessTokenUseAdmin(ModelAdmin):
    list_display = ('token', 'timestamp', 'client_ip', 'client_user_agent')

site.register(AccessToken, AccessTokenAdmin)
site.register(AccessTokenUse, AccessTokenUseAdmin)
