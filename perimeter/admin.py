# -*- coding: utf-8 -*-
"""Django models for the Perimeter app."""
from django.contrib.admin import site, ModelAdmin

from perimeter.models import AccessToken, AccessTokenUse


class AccessTokenAdmin(ModelAdmin):

    raw_id_fields = ('created_by',)
    list_display = ('token', 'expires_on', 'is_active', 'created_at', 'created_by')

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


class AccessTokenUseAdmin(ModelAdmin):
    list_display = ('token', 'user_name', 'timestamp', 'client_ip')


site.register(AccessToken, AccessTokenAdmin)
site.register(AccessTokenUse, AccessTokenUseAdmin)
