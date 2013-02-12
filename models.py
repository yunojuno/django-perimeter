"""
Django models for the Perimeter app.
"""
from django.db import models
from django.contrib.admin import site, ModelAdmin
from django.contrib.auth.models import User
from datetime import date, timedelta


def tomorrow():
    """
    Return tomorrow's date (helper function).
    """
    return date.today() + timedelta(days=1)


class AccessToken(models.Model):
    """
    A token that allows a user entry to the site via Perimeter.
    """
    class Meta:
        verbose_name = u'Access token'
        verbose_name_plural = u'Access tokens'

    email = models.EmailField(verbose_name='Token recipient')
    token = models.CharField(max_length=10, unique=True)
    expires_at = models.DateField(default=tomorrow())
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True)

    def has_expired(self):
        """ Indicate whether the token is still valid or not. """
        return date.today() > self.expires_at

    def is_valid(self):
        """
        Is the token still valid or not .

        At the moment this is just the inverse of has_expired, but at some point
        this may include other properties of the token beyond its expiry date.
        """
        return not self.has_expired()

    def record_usage(self, client_ip='0.0.0.0', client_user_agent='unknown'):
        """
        Write out a log record that this token has been used by someone.
        """
        atu = AccessTokenUsage(
            token=self,
            client_ip=client_ip,
            client_user_agent=client_user_agent
        )
        atu.save()

    def __unicode__(self):
        return u"%s <%s>" % (self.token, self.email)

    def __str__(self):
        return self.__unicode__().encode('UTF-8')


class AccessTokenAdmin(ModelAdmin):

    raw_id_fields = ('created_by',)
    list_display = ('token', 'email', 'created_at', 'created_by')

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


class AccessTokenUsage(models.Model):
    """
    Audit record used to log whenever an access token is used (see below).

    Auditing whenever a token is used would be excessive, so instead we log
    whenever the token is first seen on a specific machine - i.e. when the
    middleware has to look the token up in the database. We record the IP
    address of the user, and their user agent, just in case.
    """
    class Meta:
        verbose_name = u'Access token use'
        verbose_name_plural = u'Access token uses'

    token = models.ForeignKey(AccessToken)
    timestamp = models.DateTimeField(auto_now_add=True)
    client_ip = models.CharField(max_length=15,
        verbose_name='IP address')
    client_user_agent = models.CharField(max_length=150,
        verbose_name="User Agent")

    def __unicode__(self):
        return u"Token '%s' used at %s" % (self.token.token, self.timestamp)

    def __str__(self):
        return self.__unicode__().encode('UTF-8')


class AccessTokenUsageAdmin(ModelAdmin):
    list_display = ('token', 'timestamp', 'client_ip', 'client_user_agent')

site.register(AccessToken, AccessTokenAdmin)
site.register(AccessTokenUsage, AccessTokenUsageAdmin)
