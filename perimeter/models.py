# -*- coding: utf-8 -*-
"""
Django models for the Perimeter app.
"""
from datetime import date, timedelta

from django.contrib.admin import site, ModelAdmin
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


def tomorrow():
    """
    Return tomorrow's date (helper function).
    """
    return date.today() + timedelta(days=1)


class AccessToken(models.Model):
    """
    A token that allows a user entry to the site via Perimeter.
    """
    token = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    expires_on = models.DateField(default=tomorrow())
    created_by = models.ForeignKey(User, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __unicode__(self):
        return u"Access token: %s" % self.token

    def __str__(self):
        return self.__unicode__().encode('UTF-8')

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
    list_display = ('token', 'created_at', 'created_by')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Presets the 'created_by' field to the current user.

        Taken from http://stackoverflow.com/a/5633217
        """
        if db_field.name == 'created_by':
            kwargs['initial'] = request.user.id
        return super(AccessTokenAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


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
